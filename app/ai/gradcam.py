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
    heatmap_path = generator.generate(image_path, model, prediction)
"""

import os
import logging

from app.ai.model_config import (
    GRADCAM_LAYER_NAME,
    GRADCAM_COLORMAP,
    GRADCAM_ALPHA,
    HEATMAP_OUTPUT_DIR,
    IMAGE_SIZE,
)

logger = logging.getLogger(__name__)


class GradCAMGenerator:
    """
    Generate Grad-CAM heatmap overlays for model explainability.

    Parameters
    ----------
    layer_name : str
        Name of the target convolutional layer. Default from model_config.
    colormap : str
        Matplotlib colormap name. Default 'jet'.
    alpha : float
        Heatmap overlay transparency (0.0 – 1.0). Default 0.4.
    output_dir : str
        Directory to save generated heatmaps.

    Methods
    -------
    generate(image_path, model, predicted_class_index)
        Generate and save a Grad-CAM heatmap overlay.
    compute_heatmap(image_tensor, model, class_index)
        Compute the raw Grad-CAM heatmap array.
    overlay_heatmap(original_image, heatmap)
        Overlay the heatmap on the original image.
    """

    def __init__(self, layer_name=None, colormap=None, alpha=None,
                 output_dir=None):
        self.layer_name = layer_name or GRADCAM_LAYER_NAME
        self.colormap = colormap or GRADCAM_COLORMAP
        self.alpha = alpha or GRADCAM_ALPHA
        self.output_dir = output_dir or HEATMAP_OUTPUT_DIR

    def generate(self, image_path, model, predicted_class_index):
        """
        Generate a Grad-CAM heatmap and save it as an overlay image.

        Parameters
        ----------
        image_path : str
            Path to the original histopathology image.
        model : tf.keras.Model
            The loaded EfficientNetB0 model.
        predicted_class_index : int
            Index of the predicted class for Grad-CAM targeting.

        Returns
        -------
        str
            Absolute path to the saved heatmap overlay image.
        """
        import tensorflow as tf
        import numpy as np
        import cv2
        from app.ai.preprocessor import ImagePreprocessor

        os.makedirs(self.output_dir, exist_ok=True)
        
        # 1. Load and preprocess the image
        preprocessor = ImagePreprocessor()
        image_tensor = preprocessor.preprocess(image_path)
        
        # 2. Compute heatmap
        heatmap = self.compute_heatmap(image_tensor, model, predicted_class_index)
        
        # 3. Load original image for overlay
        original_image = cv2.imread(image_path)
        if original_image is None:
            from PIL import Image
            pil_img = Image.open(image_path).convert('RGB')
            original_image = np.array(pil_img)
            # Convert RGB to BGR for cv2 saving
            original_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR)
            
        # 4. Apply colormap and overlay on original image
        overlay = self.overlay_heatmap(original_image, heatmap)
        
        # 5. Save to HEATMAP_OUTPUT_DIR
        import uuid
        heatmap_filename = f'gradcam_{uuid.uuid4().hex[:8]}.jpg'
        heatmap_path = os.path.join(self.output_dir, heatmap_filename)
        cv2.imwrite(heatmap_path, overlay)
        
        # Return path relative to static/ or however it is served. Wait, it is in data/heatmaps.
        # Flask usually serves from data/heatmaps or static. Let's return absolute path or basename.
        # The prompt says 'heatmap_path : str - path to Grad-CAM heatmap overlay'. 
        return heatmap_path

    def compute_heatmap(self, image_tensor, model, class_index):
        import tensorflow as tf
        import numpy as np
        
        # Initialize model inputs to avoid 'layer sequential has never been called' error
        _ = model(tf.zeros((1, 224, 224, 3)))
        
        base_model = model.layers[0]
        target_layer = base_model.get_layer(self.layer_name)
        
        grad_model = tf.keras.models.Model(
            inputs=base_model.inputs,
            outputs=[target_layer.output, base_model.output]
        )

        with tf.GradientTape() as tape:
            conv_outputs, base_output = grad_model(image_tensor)
            
            # Forward pass through the rest of the Sequential model
            x = base_output
            for layer in model.layers[1:]:
                x = layer(x)
            predictions = x
            
            loss = predictions[:, class_index]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
        return heatmap.numpy()

    def overlay_heatmap(self, original_image, heatmap):
        import cv2
        import numpy as np
        
        # Resize heatmap to match original image
        heatmap = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
        
        # Superimpose
        overlay = cv2.addWeighted(original_image, 1 - self.alpha, heatmap_colored, self.alpha, 0)
        return overlay
