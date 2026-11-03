"""
ColonSightAI — Genuine Real Model & Grad-CAM Integration Tests
==============================================================

These integration tests use the ACTUAL trained EfficientNetB0 model
(trained_models/efficientnetb0_colon.h5) without mocking the deep learning
computations.

They verify:
1. Genuine Grad-CAM heatmap computation on the real model (classes 0 and 1).
2. Genuine layer resolution for 'top_conv' inside the nested EfficientNetB0 graph.
3. Dimensional matching between input image and saved Grad-CAM overlay.
4. End-to-end remote inference flow with the real model, validating prediction
   probabilities, class mapping, and decodable Grad-CAM Base64 output.
"""

import os
import io
import cv2
import json
import base64
import pytest
import numpy as np

from app.ai.model_config import (
    MODEL_PATH,
    CLASS_LABELS,
    CLASS_DISPLAY_NAMES,
    GRADCAM_LAYER_NAME,
)
from app.ai.gradcam import GradCAMGenerator
from app.ai.predictor import Predictor


def _load_real_model_or_skip():
    """Helper to load the real model or skip test if unavailable."""
    if not os.path.exists(MODEL_PATH):
        pytest.skip(f"Trained model not found at {MODEL_PATH}")

    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        pytest.skip(f"Could not load TensorFlow or model file: {e}")


@pytest.fixture(scope="module")
def real_model():
    """Module-level fixture to load the actual trained EfficientNetB0 model once."""
    return _load_real_model_or_skip()


@pytest.fixture
def sample_histology_image(tmp_path):
    """Generate a realistic test histology image in H&E stain tones."""
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    # Background stromal pink
    img[:, :, 0] = 170  # B
    img[:, :, 1] = 90   # G
    img[:, :, 2] = 210  # R
    # Add simulated hyperchromatic nuclei clusters (dark purple/blue)
    for center in [(60, 60), (150, 160), (90, 140), (170, 70)]:
        cv2.circle(img, center, 22, (130, 30, 80), -1)

    img_path = str(tmp_path / "test_histology_slide.jpg")
    cv2.imwrite(img_path, img)
    return img_path, img


class TestGradCAMRealModelIntegration:
    """Integration tests running genuine Grad-CAM on the real EfficientNetB0 model."""

    def test_genuine_gradcam_heatmap_class_0_cancerous(self, real_model, sample_histology_image):
        """Verify real Grad-CAM computation targeting class 0 (colon_aca)."""
        img_path, orig_img = sample_histology_image
        generator = GradCAMGenerator(layer_name=GRADCAM_LAYER_NAME)

        from app.ai.preprocessor import ImagePreprocessor
        preprocessor = ImagePreprocessor()
        tensor = preprocessor.preprocess(img_path)

        heatmap = generator.compute_heatmap(tensor, real_model, class_index=0)

        # 1. Output shape must match the spatial dimensions of top_conv (7 x 7)
        assert heatmap.shape == (7, 7), f"Expected (7, 7) heatmap, got {heatmap.shape}"

        # 2. Values must be strictly bounded in [0.0, 1.0]
        assert np.min(heatmap) >= 0.0, "Heatmap minimum must be >= 0.0"
        assert np.max(heatmap) <= 1.0, "Heatmap maximum must be <= 1.0"

        # 3. Must NEVER produce NaN or Inf
        assert not np.isnan(heatmap).any(), "Heatmap contains NaN values"
        assert not np.isinf(heatmap).any(), "Heatmap contains Inf values"

    def test_genuine_gradcam_heatmap_class_1_normal(self, real_model, sample_histology_image):
        """Verify real Grad-CAM computation targeting class 1 (colon_n)."""
        img_path, orig_img = sample_histology_image
        generator = GradCAMGenerator(layer_name=GRADCAM_LAYER_NAME)

        from app.ai.preprocessor import ImagePreprocessor
        preprocessor = ImagePreprocessor()
        tensor = preprocessor.preprocess(img_path)

        heatmap = generator.compute_heatmap(tensor, real_model, class_index=1)

        assert heatmap.shape == (7, 7)
        assert np.min(heatmap) >= 0.0
        assert np.max(heatmap) <= 1.0
        assert not np.isnan(heatmap).any()
        assert not np.isinf(heatmap).any()

    def test_genuine_gradcam_overlay_generation_and_saving(self, real_model, sample_histology_image, tmp_path):
        """Verify end-to-end generation and disk persistence of overlay using real model."""
        img_path, orig_img = sample_histology_image
        out_dir = str(tmp_path / "heatmaps")
        generator = GradCAMGenerator(output_dir=out_dir)

        saved_path = generator.generate(img_path, real_model, predicted_class_index=0)

        assert os.path.exists(saved_path), "Grad-CAM overlay file was not saved"
        saved_img = cv2.imread(saved_path)
        assert saved_img is not None, "Saved overlay could not be read back"
        assert saved_img.shape == orig_img.shape, (
            f"Saved overlay shape {saved_img.shape} must match original {orig_img.shape}"
        )


class TestRemoteInferenceRealModelIntegration:
    """Integration tests running the complete remote inference flow with the real model."""

    def test_remote_inference_server_complete_flow(self, real_model, sample_histology_image, tmp_path):
        """Verify real model inference via colab_inference_server endpoints."""
        from scripts.colab_inference_server import app as remote_app, load_inference_model

        # Ensure server has real model loaded
        load_inference_model(MODEL_PATH)
        client = remote_app.test_client()

        img_path, orig_img = sample_histology_image
        with open(img_path, 'rb') as f:
            img_bytes = f.read()

        response = client.post(
            '/predict',
            data={'file': (io.BytesIO(img_bytes), 'slide.jpg')},
            content_type='multipart/form-data'
        )

        assert response.status_code == 200, f"Remote inference failed with status {response.status_code}"
        data = response.json

        # 1. Verify predicted class is a valid trained class
        assert data['predicted_class'] in ['colon_aca', 'colon_n']
        assert data['display_name'] in [CLASS_DISPLAY_NAMES['colon_aca'], CLASS_DISPLAY_NAMES['colon_n']]

        # 2. Verify genuine probabilities sum to ~1.0
        probs = data['all_probabilities']
        assert 'colon_aca' in probs and 'colon_n' in probs
        prob_sum = probs['colon_aca'] + probs['colon_n']
        assert prob_sum == pytest.approx(1.0, abs=1e-2)

        # 3. Verify confidence matches predicted class probability
        assert data['confidence'] == pytest.approx(probs[data['predicted_class']], abs=1e-4)

        # 4. Verify Grad-CAM Base64 data is a valid decodable image matching input dimensions
        assert 'heatmap_base64' in data and len(data['heatmap_base64']) > 0
        raw_heatmap_bytes = base64.b64decode(data['heatmap_base64'])
        heatmap_img = cv2.imdecode(np.frombuffer(raw_heatmap_bytes, np.uint8), cv2.IMREAD_COLOR)
        assert heatmap_img is not None, "Remote heatmap Base64 is not decodable as an image"
        assert heatmap_img.shape == orig_img.shape, (
            f"Remote heatmap shape {heatmap_img.shape} must match input {orig_img.shape}"
        )

        # 5. Verify client Predictor and GradCAMGenerator consume this real remote response seamlessly
        predictor = Predictor()
        gradcam = GradCAMGenerator(output_dir=str(tmp_path / "remote_heatmaps"))

        # Test Predictor._predict_remote with mock requests pointing to the test client
        from unittest.mock import patch, MagicMock
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = data
        mock_resp.raise_for_status = MagicMock()

        with patch.dict('os.environ', {'REMOTE_INFERENCE_URL': 'http://test-server/predict'}):
            with patch('requests.post', return_value=mock_resp):
                client_result = predictor.predict(np.zeros((1, 224, 224, 3)), image_path=img_path)

                assert client_result['predicted_class'] == data['predicted_class']
                assert client_result['confidence'] == data['confidence']

                # Test GradCAMGenerator consumes and persists remote heatmap
                target_idx = 0 if client_result['predicted_class'] == 'colon_aca' else 1
                saved_heatmap = gradcam.generate(
                    img_path,
                    model=None,
                    predicted_class_index=target_idx,
                    last_prediction_result=client_result
                )
                assert os.path.exists(saved_heatmap)
                read_overlay = cv2.imread(saved_heatmap)
                assert read_overlay.shape == orig_img.shape

