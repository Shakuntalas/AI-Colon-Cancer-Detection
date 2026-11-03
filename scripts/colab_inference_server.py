"""
ColonSightAI — Google Colab & Remote Inference Server
=====================================================

This script allows hosting the TensorFlow EfficientNetB0 model and Grad-CAM
explainability engine in an approved Linux/Cloud environment (such as Google Colab,
Google Cloud Run, or AWS EC2), completely isolating TensorFlow from Windows Code
Integrity / Smart App Control policies.

How to run on Google Colab:
---------------------------
1. Upload your model: `trained_models/efficientnetb0_colon.h5` to Google Colab.
2. Install dependencies:
       !pip install flask pyngrok tensorflow pillow opencv-python-headless
3. Run this server script:
       python colab_inference_server.py --model efficientnetb0_colon.h5 --ngrok-token <YOUR_TOKEN>
4. Copy the generated public URL (e.g., https://xxxx.ngrok-free.app).
5. In your local Windows ColonSightAI `.env` file, set:
       REMOTE_INFERENCE_URL=https://xxxx.ngrok-free.app/predict
6. Start your local Flask app:
       python run.py
   All predictions and Grad-CAM heatmaps will be computed seamlessly on Colab!
"""

import os
import sys
import time
import base64
import argparse
import numpy as np
import cv2
from io import BytesIO
from PIL import Image

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Flask is not installed. Install with: pip install flask")
    sys.exit(1)

try:
    import tensorflow as tf
except ImportError:
    print("TensorFlow is not installed. Install with: pip install tensorflow")
    sys.exit(1)

app = Flask(__name__)

# Constants matching ColonSightAI configuration
MODEL = None
IMAGE_SIZE = (224, 224)
CLASS_LABELS = {0: 'colon_aca', 1: 'colon_n'}
CLASS_DISPLAY_NAMES = {
    'colon_aca': 'Colon Adenocarcinoma',
    'colon_n': 'Colon Normal Tissue',
}
GRADCAM_LAYER_NAME = 'top_conv'


def load_inference_model(model_path):
    """Load and warm up the EfficientNetB0 Keras model."""
    global MODEL
    print(f"[*] Loading model from {model_path}...")
    MODEL = tf.keras.models.load_model(model_path)
    # Warm up model graph
    _ = MODEL(tf.zeros((1, 224, 224, 3)))
    print(f"[OK] Model loaded successfully. Input: {MODEL.input_shape}, Output: {MODEL.output_shape}")


def preprocess_image(image_bytes):
    """Decode and preprocess image bytes to (1, 224, 224, 3) float32 tensor."""
    pil_img = Image.open(BytesIO(image_bytes)).convert('RGB')
    orig_np = np.array(pil_img)

    resized = cv2.resize(orig_np, IMAGE_SIZE)
    tensor = np.expand_dims(resized.astype(np.float32), axis=0)
    return tensor, orig_np


def compute_gradcam(image_tensor, original_image_np, class_index):
    """Compute Grad-CAM heatmap and overlay on original image safely without NaNs."""
    # Locate base model
    base_model = None
    base_idx = -1
    for idx, layer in enumerate(MODEL.layers):
        if hasattr(layer, 'get_layer'):
            try:
                _ = layer.get_layer(GRADCAM_LAYER_NAME)
                base_model = layer
                base_idx = idx
                break
            except ValueError:
                continue

    if base_model is not None:
        target_layer = base_model.get_layer(GRADCAM_LAYER_NAME)
        grad_model = tf.keras.models.Model(
            inputs=base_model.inputs,
            outputs=[target_layer.output, base_model.output]
        )
        inputs_to_feed = [image_tensor] if isinstance(grad_model.inputs, list) and not isinstance(image_tensor, list) else image_tensor
        with tf.GradientTape() as tape:
            conv_outputs, base_output = grad_model(inputs_to_feed)
            x = base_output
            for layer in MODEL.layers[base_idx + 1:]:
                x = layer(x)
            predictions = x
            if predictions.shape[-1] == 1:
                loss = predictions[:, 0] if class_index == 1 else (1.0 - predictions[:, 0])
            else:
                loss = predictions[:, class_index]

        grads = tape.gradient(loss, conv_outputs)
        if grads is None:
            grads = tf.zeros_like(conv_outputs)
        grads = tf.where(tf.math.is_nan(grads), tf.zeros_like(grads), grads)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        pooled_grads = tf.where(tf.math.is_nan(pooled_grads), tf.zeros_like(pooled_grads), pooled_grads)

        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0.0)

        max_val = tf.math.reduce_max(heatmap)
        max_float = float(max_val)
        if np.isnan(max_float) or max_float <= 1e-10:
            heatmap = tf.zeros_like(heatmap)
        else:
            heatmap = heatmap / max_val
        heatmap_np = heatmap.numpy()
    else:
        heatmap_np = np.zeros((7, 7), dtype=np.float32)

    heatmap_np = np.nan_to_num(heatmap_np, nan=0.0, posinf=1.0, neginf=0.0)
    heatmap_np = np.clip(heatmap_np, 0.0, 1.0)

    # Resize heatmap to match original image dimensions
    heatmap_resized = cv2.resize(heatmap_np, (original_image_np.shape[1], original_image_np.shape[0]))
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
    heatmap_colored_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    # Superimpose heatmap onto original image
    alpha = 0.4
    overlay = cv2.addWeighted(original_image_np, 1 - alpha, heatmap_colored_rgb, alpha, 0)
    return overlay


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL is not None,
        'framework': 'TensorFlow',
        'tf_version': tf.__version__,
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Run model prediction and Grad-CAM explainability on uploaded image."""
    if 'file' not in request.files and not request.data:
        return jsonify({'error': 'No file provided'}), 400

    if 'file' in request.files:
        image_bytes = request.files['file'].read()
    else:
        image_bytes = request.data

    try:
        tensor, original_np = preprocess_image(image_bytes)

        start_time = time.perf_counter()
        predictions = MODEL.predict(tensor, verbose=0)
        inference_time = (time.perf_counter() - start_time) * 1000

        pred_idx = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][pred_idx])
        predicted_class = CLASS_LABELS.get(pred_idx, 'colon_aca')

        # Determine confidence level
        if confidence >= 0.85:
            confidence_level = 'high'
        elif confidence >= 0.60:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'

        # Compute Grad-CAM
        overlay_rgb = compute_gradcam(tensor, original_np, pred_idx)
        overlay_bgr = cv2.cvtColor(overlay_rgb, cv2.COLOR_RGB2BGR)

        # Encode heatmap to base64
        _, buffer = cv2.imencode('.jpg', overlay_bgr)
        heatmap_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'predicted_class': predicted_class,
            'display_name': CLASS_DISPLAY_NAMES[predicted_class],
            'confidence': round(confidence, 4),
            'confidence_level': confidence_level,
            'all_probabilities': {
                CLASS_LABELS[i]: round(float(p), 4)
                for i, p in enumerate(predictions[0])
            },
            'inference_time_ms': round(inference_time, 2),
            'model_version': '1.0.0',
            'heatmap_base64': heatmap_base64,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ColonSightAI Remote Inference Server')
    parser.add_argument('--model', default='trained_models/efficientnetb0_colon.h5', help='Path to .h5 model file')
    parser.add_argument('--port', type=int, default=5001, help='Port to run server on')
    parser.add_argument('--ngrok-token', default=None, help='Optional ngrok auth token for public tunnel')
    args = parser.parse_args()

    load_inference_model(args.model)

    if args.ngrok_token:
        try:
            from pyngrok import ngrok
            ngrok.set_auth_token(args.ngrok_token)
            public_url = ngrok.connect(args.port).public_url
            print(f"\n========================================================")
            print(f" [*] PUBLIC INFERENCE URL: {public_url}/predict")
            print(f" Set in Windows .env: REMOTE_INFERENCE_URL={public_url}/predict")
            print(f"========================================================\n")
        except Exception as err:
            print(f"Could not initialize ngrok: {err}")

    app.run(host='0.0.0.0', port=args.port)

