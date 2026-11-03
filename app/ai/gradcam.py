"""
ColonSightAI — Grad-CAM Explainability
=========================================

Generates Gradient-weighted Class Activation Mapping (Grad-CAM)
heatmap overlays for model interpretability.

Grad-CAM visualises which regions of the histopathology image most
influenced the model's classification decision, enabling clinicians
to understand and trust the AI prediction.

Reference:
    Selvaraju et al., "Grad-CAM: Visual Explanations from Deep Networks
    via Gradient-based Localization", ICCV 2017.

Usage:
    from app.ai.gradcam import GradCAMGenerator

    generator = GradCAMGenerator()
    heatmap_path = generator.generate(image_path, model, predicted_class_index)
"""

import os
import uuid
import logging
import numpy as np
import cv2

from app.ai.model_config import (
    GRADCAM_LAYER_NAME,
    GRADCAM_COLORMAP,
    GRADCAM_ALPHA,
    HEATMAP_OUTPUT_DIR,
)

logger = logging.getLogger(__name__)


class GradCAMGenerator:
    """
    Generate Grad-CAM heatmap overlays for model explainability.

    Parameters
    ----------
    layer_name : str, optional
        Name of the target convolutional layer. Default from model_config ('top_conv').
    colormap : str, optional
        OpenCV colormap identifier or name. Default 'jet' (COLORMAP_JET).
    alpha : float, optional
        Heatmap overlay transparency (0.0 – 1.0). Default 0.4.
    output_dir : str, optional
        Directory to save generated heatmaps.
    """

    def __init__(self, layer_name=None, colormap=None, alpha=None,
                 output_dir=None):
        self.layer_name = layer_name or GRADCAM_LAYER_NAME
        self.colormap = colormap or GRADCAM_COLORMAP
        self.alpha = float(alpha if alpha is not None else GRADCAM_ALPHA)
        self.output_dir = output_dir or HEATMAP_OUTPUT_DIR

    def generate(self, image_path, model=None, predicted_class_index=0, last_prediction_result=None):
        """
        Generate a Grad-CAM heatmap and save it as an overlay image.

        Parameters
        ----------
        image_path : str
            Path to the original histopathology image.
        model : tf.keras.Model, optional
            The loaded EfficientNetB0 model.
        predicted_class_index : int
            Index of the predicted class for Grad-CAM targeting.
        last_prediction_result : dict, optional
            Result dict from predictor, which may contain a remote heatmap base64 string.

        Returns
        -------
        str
            Absolute path to the saved heatmap overlay image.

        Raises
        ------
        InferenceError
            If model is unavailable and no remote Grad-CAM output was provided.
        FileNotFoundError
            If image_path does not exist.
        ValueError
            If predicted_class_index is invalid.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at: {image_path}")

        os.makedirs(self.output_dir, exist_ok=True)
        heatmap_filename = f'gradcam_{uuid.uuid4().hex[:8]}.jpg'
        heatmap_path = os.path.join(self.output_dir, heatmap_filename)

        # 1. Check if genuine remote inference supplied the heatmap
        if last_prediction_result and last_prediction_result.get('heatmap_base64'):
            import base64
            b64_str = last_prediction_result['heatmap_base64']
            try:
                img_data = base64.b64decode(b64_str, validate=True)
            except Exception as e:
                raise ValueError(f"Invalid Base64 encoding in remote heatmap: {e}") from e

            # Decode as actual image using OpenCV to verify image integrity
            np_arr = np.frombuffer(img_data, np.uint8)
            decoded_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if decoded_image is None or decoded_image.size == 0:
                raise ValueError("Remote heatmap Base64 does not contain a valid, decodable image.")

            # Save the verified, decoded image
            cv2.imwrite(heatmap_path, decoded_image)
            logger.info("Validated and saved genuine remote Grad-CAM heatmap to: %s", heatmap_path)
            return heatmap_path

        # 2. Check if local model is available for genuine local Grad-CAM
        if model is None:
            from app.ai.predictor import InferenceError
            raise InferenceError(
                "Grad-CAM explainability failed: EfficientNetB0 model is not available "
                "and no remote Grad-CAM heatmap was provided."
            )

        # Load and preprocess image for model input
        from app.ai.preprocessor import ImagePreprocessor
        preprocessor = ImagePreprocessor()
        image_tensor = preprocessor.preprocess(image_path)

        # Compute genuine Grad-CAM heatmap
        heatmap = self.compute_heatmap(image_tensor, model, predicted_class_index)

        # Load original image for overlay
        original_image = cv2.imread(image_path)
        if original_image is None:
            from PIL import Image
            pil_img = Image.open(image_path).convert('RGB')
            original_image = np.array(pil_img)
            original_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)

        # Overlay heatmap on original image and save
        overlay = self.overlay_heatmap(original_image, heatmap)
        cv2.imwrite(heatmap_path, overlay)
        logger.info("Generated and saved genuine local Grad-CAM overlay to: %s", heatmap_path)
        return heatmap_path

    def _find_target_layer(self, model):
        """
        Locate the target convolutional layer within the model or nested sub-models.

        Returns
        -------
        tuple (layer, sub_model, sub_model_index)
            - layer: Target tf.keras.layers.Layer
            - sub_model: Nested sub-model containing the layer, or None
            - sub_model_index: Index of sub_model in model.layers, or -1
        """
        # 1. Check if target layer is directly in root model
        try:
            layer = model.get_layer(self.layer_name)
            return layer, None, -1
        except (ValueError, AttributeError):
            pass

        # 2. Search nested sub-models (e.g. 'efficientnetb0' inside Sequential)
        if hasattr(model, 'layers'):
            for idx, layer in enumerate(model.layers):
                if hasattr(layer, 'get_layer'):
                    try:
                        target = layer.get_layer(self.layer_name)
                        return target, layer, idx
                    except ValueError:
                        continue

        # 3. Target layer not found
        available = []
        if hasattr(model, 'layers'):
            for l in model.layers:
                available.append(l.name)
                if hasattr(l, 'layers'):
                    available.extend([f"{l.name}.{sl.name}" for sl in l.layers[-10:]])
        raise ValueError(
            f"Target layer '{self.layer_name}' not found in model or nested sub-models. "
            f"Available layers include: {available[:15]}..."
        )

    def compute_heatmap(self, image_tensor, model, class_index):
        """
        Compute the raw 2D Grad-CAM heatmap for a target class using tf.GradientTape.

        Parameters
        ----------
        image_tensor : tf.Tensor or numpy.ndarray
            Input image tensor with shape (1, 224, 224, 3).
        model : tf.keras.Model
            The trained EfficientNetB0 classification model.
        class_index : int
            Index of the target class to compute gradients for.

        Returns
        -------
        numpy.ndarray
            Normalized 2D heatmap with shape (H, W), values in [0.0, 1.0].
        """
        try:
            import tensorflow as tf
        except (ImportError, OSError) as err:
            from app.ai.predictor import InferenceError
            raise InferenceError(
                f"TensorFlow is required for local Grad-CAM computation: {err}"
            ) from err

        # Verify target layer exists in model architecture
        target_layer, sub_model, sub_model_idx = self._find_target_layer(model)

        # Build Grad-CAM multi-output model
        if sub_model is None:
            grad_model = tf.keras.models.Model(
                inputs=model.inputs,
                outputs=[target_layer.output, model.output]
            )
            inputs_to_feed = [image_tensor] if isinstance(grad_model.inputs, list) and not isinstance(image_tensor, list) else image_tensor
            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(inputs_to_feed)
                loss = self._compute_class_loss(predictions, class_index)
        else:
            grad_model = tf.keras.models.Model(
                inputs=sub_model.inputs,
                outputs=[target_layer.output, sub_model.output]
            )
            inputs_to_feed = [image_tensor] if isinstance(grad_model.inputs, list) and not isinstance(image_tensor, list) else image_tensor
            with tf.GradientTape() as tape:
                conv_outputs, sub_out = grad_model(inputs_to_feed)
                x = sub_out
                for layer in model.layers[sub_model_idx + 1:]:
                    x = layer(x)
                predictions = x
                loss = self._compute_class_loss(predictions, class_index)

        # Compute gradients of target class score with respect to target feature maps
        grads = tape.gradient(loss, conv_outputs)
        if grads is None:
            from app.ai.predictor import InferenceError
            raise InferenceError(
                f"Grad-CAM error: No gradients were computed for target layer '{self.layer_name}'."
            )

        # Handle NaNs or Infs in gradients safely
        grads = tf.where(tf.math.is_nan(grads), tf.zeros_like(grads), grads)
        grads = tf.where(tf.math.is_inf(grads), tf.zeros_like(grads), grads)

        # Global average pooling of gradients: α_k^c = mean(∂y^c / ∂A^k)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        pooled_grads = tf.where(tf.math.is_nan(pooled_grads), tf.zeros_like(pooled_grads), pooled_grads)

        # Weight feature maps by pooled gradients: L_Grad-CAM = ReLU(Σ α_k^c A^k)
        conv_outputs = conv_outputs[0]  # Shape (H, W, C)
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)

        # Apply ReLU to retain only positive influences on the target class
        heatmap = tf.maximum(heatmap, 0.0)

        # Safe normalization to [0.0, 1.0] preventing division by zero and NaNs
        max_val = tf.math.reduce_max(heatmap)
        max_float = float(max_val)
        if np.isnan(max_float) or max_float <= 1e-10:
            logger.warning(
                "Grad-CAM computed zero or near-zero gradient activation for class index %d.",
                class_index
            )
            heatmap = tf.zeros_like(heatmap)
        else:
            heatmap = heatmap / max_val

        heatmap_np = heatmap.numpy()
        heatmap_np = np.nan_to_num(heatmap_np, nan=0.0, posinf=1.0, neginf=0.0)
        heatmap_np = np.clip(heatmap_np, 0.0, 1.0)
        return heatmap_np.astype(np.float32)

    @staticmethod
    def _compute_class_loss(predictions, class_index):
        """
        Extract the target loss tensor for the specified class index.
        Safely validates class index against prediction shape.
        """
        num_classes = int(predictions.shape[-1])
        if num_classes == 1:
            if class_index == 1:
                return predictions[:, 0]
            elif class_index == 0:
                return 1.0 - predictions[:, 0]
            else:
                raise ValueError(
                    f"Invalid class_index {class_index} for single-output binary model."
                )
        else:
            if class_index < 0 or class_index >= num_classes:
                raise ValueError(
                    f"Invalid class_index {class_index}. Model output has {num_classes} classes."
                )
            return predictions[:, class_index]

    def overlay_heatmap(self, original_image, heatmap):
        """
        Superimpose the Grad-CAM heatmap onto the original image.

        Ensures that heatmap dimensions and overlay match the original image.

        Parameters
        ----------
        original_image : numpy.ndarray
            Original image array with shape (H, W, 3) in BGR format.
        heatmap : numpy.ndarray
            2D heatmap array with values in [0.0, 1.0].

        Returns
        -------
        numpy.ndarray
            Superimposed image overlay with shape (H, W, 3) matching original_image.
        """
        if original_image is None or original_image.size == 0:
            raise ValueError("original_image must be a non-empty image array")

        # Ensure heatmap is 2D and sanitized
        heatmap = np.squeeze(heatmap)
        if heatmap.ndim != 2:
            raise ValueError(f"Heatmap must be 2D after squeezing, got shape {heatmap.shape}")

        heatmap = np.nan_to_num(heatmap, nan=0.0, posinf=1.0, neginf=0.0)
        heatmap = np.clip(heatmap, 0.0, 1.0)

        # Target dimensions must match the original uploaded image exactly
        orig_height, orig_width = original_image.shape[:2]

        # Resize heatmap to original image spatial dimensions
        heatmap_resized = cv2.resize(
            heatmap,
            (orig_width, orig_height),
            interpolation=cv2.INTER_LINEAR
        )

        # Convert to 8-bit [0, 255] and apply colormap
        heatmap_uint8 = np.uint8(255.0 * heatmap_resized)
        heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

        # Blend: (1 - alpha) * original + alpha * heatmap
        alpha = max(0.0, min(1.0, float(self.alpha)))
        overlay = cv2.addWeighted(
            original_image,
            1.0 - alpha,
            heatmap_colored,
            alpha,
            0.0
        )

        # Explicit dimensional verification
        assert overlay.shape[:2] == (orig_height, orig_width), (
            f"Overlay dimensions {overlay.shape[:2]} must match original image {(orig_height, orig_width)}"
        )
        return overlay
