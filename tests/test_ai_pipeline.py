"""
ColonSightAI — AI Pipeline Tests
====================================

Tests for the AI pipeline modules (model config, preprocessor, predictor).
These are stub tests that verify the pipeline interfaces are correct.
"""

from app.ai.model_config import (
    MODEL_NAME,
    CLASS_LABELS,
    CLASS_DISPLAY_NAMES,
    IMAGE_SIZE,
    NUM_CLASSES,
    CONFIDENCE_THRESHOLD,
    DATASET_INFO,
    TRAINING_CONFIG,
)
from app.ai.model_loader import ModelLoader
from app.ai.preprocessor import ImagePreprocessor
from app.ai.predictor import Predictor, InferenceError
from app.ai.gradcam import GradCAMGenerator
import os
import requests
import numpy as np
import pytest
from unittest.mock import patch, MagicMock


class TestModelConfig:
    """Tests for AI model configuration constants."""

    def test_model_name(self):
        """Model name should be EfficientNetB0."""
        assert MODEL_NAME == 'EfficientNetB0'

    def test_image_size(self):
        """Image size should be 224x224."""
        assert IMAGE_SIZE == (224, 224)

    def test_num_classes(self):
        """Should have exactly 2 classes."""
        assert NUM_CLASSES == 2

    def test_class_labels_complete(self):
        """All class indices should have labels matching the training configuration."""
        assert 0 in CLASS_LABELS
        assert 1 in CLASS_LABELS
        assert CLASS_LABELS[0] == 'colon_aca'
        assert CLASS_LABELS[1] == 'colon_n'

    def test_class_to_index_mapping_matches_training_config(self):
        """
        Verify class-to-index mapping strictly matches training configuration:
        Index 0 -> 'colon_aca' (Colon Adenocarcinoma - cancerous)
        Index 1 -> 'colon_n'   (Colon Normal Tissue - benign)
        """
        assert CLASS_LABELS[0] == 'colon_aca'
        assert CLASS_LABELS[1] == 'colon_n'
        assert CLASS_DISPLAY_NAMES['colon_aca'] == 'Colon Adenocarcinoma'
        assert CLASS_DISPLAY_NAMES['colon_n'] == 'Colon Normal Tissue'
        assert NUM_CLASSES == 2

    def test_display_names_complete(self):
        """All classes should have display names."""
        for label in CLASS_LABELS.values():
            assert label in CLASS_DISPLAY_NAMES

    def test_confidence_threshold_range(self):
        """Confidence threshold should be between 0 and 1."""
        assert 0.0 < CONFIDENCE_THRESHOLD < 1.0

    def test_dataset_info_complete(self):
        """Dataset info should contain all required fields."""
        required = ['name', 'source', 'total_images', 'classes']
        for key in required:
            assert key in DATASET_INFO

    def test_training_config_complete(self):
        """Training config should have all hyperparameters."""
        required = ['batch_size', 'epochs', 'learning_rate', 'optimizer']
        for key in required:
            assert key in TRAINING_CONFIG


class TestModelLoader:
    """Tests for the model loader."""

    def test_singleton_pattern(self):
        """ModelLoader should always return the same instance."""
        loader1 = ModelLoader()
        loader2 = ModelLoader()
        assert loader1 is loader2

    def test_model_info(self):
        """get_model_info should return a well-formed dict."""
        loader = ModelLoader()
        info = loader.get_model_info()
        assert 'name' in info
        assert 'version' in info
        assert 'is_loaded' in info
        assert 'file_exists' in info


class TestImagePreprocessor:
    """Tests for the image preprocessor."""

    def test_default_config(self):
        """Preprocessor should use default config from model_config."""
        preprocessor = ImagePreprocessor()
        assert preprocessor.target_size == IMAGE_SIZE
        assert preprocessor.channels == 3

    def test_custom_config(self):
        """Preprocessor should accept custom configuration."""
        preprocessor = ImagePreprocessor(
            target_size=(128, 128),
            channels=1,
            scale_factor=1.0 / 127.5,
        )
        assert preprocessor.target_size == (128, 128)
        assert preprocessor.channels == 1

    def test_preprocessing_info(self):
        """get_preprocessing_info should return config summary."""
        preprocessor = ImagePreprocessor()
        info = preprocessor.get_preprocessing_info()
        assert 'target_size' in info
        assert 'channels' in info
        assert 'color_space' in info


class TestPredictor:
    """Tests for the predictor."""

    def test_interpret_confidence_high(self):
        """High confidence should be classified as 'high'."""
        assert Predictor.interpret_confidence(0.95) == 'high'

    def test_interpret_confidence_medium(self):
        """Medium confidence should be classified as 'medium'."""
        assert Predictor.interpret_confidence(0.70) == 'medium'

    def test_interpret_confidence_low(self):
        """Low confidence should be classified as 'low'."""
        assert Predictor.interpret_confidence(0.45) == 'low'

    def test_failed_remote_inference_raises_inference_error_never_fabricates(self):
        """When remote inference fails and local TF is unavailable, raise InferenceError; never fabricate."""
        predictor = Predictor()
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)

        with patch.dict('os.environ', {'REMOTE_INFERENCE_URL': 'https://invalid-colab-endpoint.local/predict'}):
            with patch('requests.post', side_effect=requests.exceptions.ConnectionError("Connection refused")):
                with patch('app.ai.model_loader.ModelLoader.get_model', return_value=None):
                    with pytest.raises(InferenceError) as exc_info:
                        predictor.predict(dummy_tensor)

                    assert "Remote inference" in str(exc_info.value)
                    assert "failed" in str(exc_info.value)
                    assert "Genuine inference is unavailable" in str(exc_info.value)

    def test_unavailable_local_model_and_no_remote_raises_inference_error(self):
        """When local model cannot load and no remote URL is set, raise InferenceError."""
        predictor = Predictor()
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)

        with patch.dict('os.environ', {}, clear=True):
            with patch('app.ai.model_loader.ModelLoader.get_model', return_value=None):
                with pytest.raises(InferenceError) as exc_info:
                    predictor.predict(dummy_tensor)

                assert "Genuine inference is unavailable" in str(exc_info.value)

    def test_remote_inference_returns_genuine_prediction(self):
        """Valid remote inference response produces genuine structured prediction."""
        import cv2
        import base64
        predictor = Predictor()
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)

        valid_heatmap_img = np.zeros((64, 64, 3), dtype=np.uint8)
        valid_heatmap_img[10:30, 10:30] = [0, 0, 255]
        _, buf = cv2.imencode('.jpg', valid_heatmap_img)
        valid_b64 = base64.b64encode(buf.tobytes()).decode('utf-8')

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'predicted_class': 'colon_aca',
            'confidence': 0.9852,
            'all_probabilities': {'colon_aca': 0.9852, 'colon_n': 0.0148},
            'model_version': '1.0.0',
            'inference_time_ms': 35.2,
            'heatmap_base64': valid_b64
        }

        with patch.dict('os.environ', {'REMOTE_INFERENCE_URL': 'https://active-colab.ngrok-free.app/predict'}):
            with patch('requests.post', return_value=mock_resp):
                result = predictor.predict(dummy_tensor)

                assert result['predicted_class'] == 'colon_aca'
                assert result['confidence'] == 0.9852
                assert result['confidence_level'] == 'high'
                assert result['all_probabilities']['colon_aca'] == 0.9852
                assert result['all_probabilities']['colon_n'] == 0.0148
                assert result['model_version'] == '1.0.0'
                assert result['heatmap_base64'] == valid_b64

    def test_remote_inference_rejects_corrupted_heatmap_base64(self):
        """Remote response with corrupted heatmap Base64 must raise InferenceError."""
        predictor = Predictor()
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'predicted_class': 'colon_aca',
            'confidence': 0.95,
            'all_probabilities': {'colon_aca': 0.95, 'colon_n': 0.05},
            'heatmap_base64': 'not_a_valid_image_payload'
        }

        with patch.dict('os.environ', {'REMOTE_INFERENCE_URL': 'https://colab.ngrok.app/predict'}):
            with patch('requests.post', return_value=mock_resp):
                with pytest.raises(InferenceError) as exc_info:
                    predictor.predict(dummy_tensor)

                assert "corrupted heatmap" in str(exc_info.value)

    def test_remote_inference_malformed_schema_rejected(self):
        """Remote response with missing or invalid fields must raise InferenceError."""
        predictor = Predictor()
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'status': 'success'}  # Missing required keys

        with patch.dict('os.environ', {'REMOTE_INFERENCE_URL': 'https://colab.ngrok.app/predict'}):
            with patch('requests.post', return_value=mock_resp):
                with patch('app.ai.model_loader.ModelLoader.get_model', return_value=None):
                    with pytest.raises(InferenceError) as exc_info:
                        predictor.predict(dummy_tensor)

                    assert "invalid schema" in str(exc_info.value)

    def test_genuine_local_model_inference(self):
        """When local model is provided, run genuine model.predict without modification."""
        predictor = Predictor()
        dummy_tensor = np.zeros((1, 224, 224, 3), dtype=np.float32)

        mock_model = MagicMock()
        # Mocking genuine model output: class 1 (colon_n) with 92% confidence
        mock_model.predict.return_value = np.array([[0.08, 0.92]], dtype=np.float32)

        result = predictor.predict(dummy_tensor, model=mock_model)

        assert result['predicted_class'] == 'colon_n'
        assert result['confidence'] == 0.92
        assert result['confidence_level'] == 'high'
        assert result['all_probabilities']['colon_n'] == 0.92
        assert result['all_probabilities']['colon_aca'] == 0.08
        mock_model.predict.assert_called_once_with(dummy_tensor, verbose=0)


class TestGradCAM:
    """Tests for Grad-CAM explainability generator."""

    def test_target_layer_verified_in_actual_model(self):
        """Verify that GRADCAM_LAYER_NAME ('top_conv') exists and is a Conv2D layer in efficientnetb0_colon.h5."""
        import h5py
        import json
        from app.ai.model_config import GRADCAM_LAYER_NAME, MODEL_PATH

        assert os.path.exists(MODEL_PATH), f"Model file must exist at {MODEL_PATH}"
        with h5py.File(MODEL_PATH, 'r') as f:
            cfg = json.loads(f.attrs['model_config'])
            base_layers = [l for l in cfg['config']['layers'] if l['config'].get('name') == 'efficientnetb0'][0]
            sub_layers = base_layers['config']['layers']
            target = [l for l in sub_layers if l['name'] == GRADCAM_LAYER_NAME]

            assert len(target) == 1, f"Layer '{GRADCAM_LAYER_NAME}' must exist in EfficientNetB0 backbone"
            assert target[0]['class_name'] == 'Conv2D', f"Target layer must be Conv2D, got {target[0]['class_name']}"

    def test_missing_target_layer_raises_value_error(self):
        """GradCAMGenerator must raise ValueError if the target layer is missing from the model."""
        gradcam = GradCAMGenerator(layer_name='non_existent_conv_layer')
        mock_model = MagicMock()
        mock_model.get_layer.side_effect = ValueError("Layer not found")
        mock_model.layers = []

        with pytest.raises(ValueError) as exc_info:
            gradcam._find_target_layer(mock_model)

        assert "non_existent_conv_layer" in str(exc_info.value)
        assert "not found in model" in str(exc_info.value)

    def test_compute_class_loss_multi_and_binary(self):
        """Ensure class loss is computed for the actual predicted class and rejects out-of-bounds indices."""
        predictions_2class = np.array([[0.1, 0.9]], dtype=np.float32)

        # Valid multi-class indices
        loss_0 = GradCAMGenerator._compute_class_loss(predictions_2class, 0)
        assert np.isclose(loss_0[0], 0.1)
        loss_1 = GradCAMGenerator._compute_class_loss(predictions_2class, 1)
        assert np.isclose(loss_1[0], 0.9)

        # Invalid multi-class index
        with pytest.raises(ValueError) as exc_info:
            GradCAMGenerator._compute_class_loss(predictions_2class, 5)
        assert "Invalid class_index 5" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            GradCAMGenerator._compute_class_loss(predictions_2class, -1)
        assert "Invalid class_index -1" in str(exc_info.value)

        # Binary output (1 unit)
        predictions_binary = np.array([[0.85]], dtype=np.float32)
        loss_bin_1 = GradCAMGenerator._compute_class_loss(predictions_binary, 1)
        assert np.isclose(loss_bin_1[0], 0.85)
        loss_bin_0 = GradCAMGenerator._compute_class_loss(predictions_binary, 0)
        assert np.isclose(loss_bin_0[0], 0.15)

    def test_zero_gradients_handling_prevents_nan(self):
        """When gradients are all zeros, compute_heatmap must produce zeros and NEVER produce NaNs."""
        generator = GradCAMGenerator(layer_name='top_conv')
        mock_tf, mock_model = self._setup_mock_grad_model()

        tape_zero = MagicMock()
        tape_zero.gradient = MagicMock(return_value=MockTFTensor(np.zeros((1, 7, 7, 16), dtype=np.float32)))
        mock_tf.GradientTape.return_value.__enter__.return_value = tape_zero

        with patch.dict('sys.modules', {'tensorflow': mock_tf}):
            heatmap = generator.compute_heatmap(np.zeros((1, 224, 224, 3)), mock_model, class_index=0)

            assert heatmap.shape == (7, 7)
            assert not np.isnan(heatmap).any(), "Heatmap must not contain NaN"
            assert not np.isinf(heatmap).any(), "Heatmap must not contain Inf"
            assert np.all(heatmap == 0.0), "Heatmap must be all zeros when gradients are zero"

    def test_nan_gradient_handling_prevents_nan(self):
        """When gradients contain NaNs, compute_heatmap must sanitize them safely."""
        generator = GradCAMGenerator(layer_name='top_conv')
        mock_tf, mock_model = self._setup_mock_grad_model()

        grad_with_nans = np.full((1, 7, 7, 16), np.nan, dtype=np.float32)
        tape_nan = MagicMock()
        tape_nan.gradient = MagicMock(return_value=MockTFTensor(grad_with_nans))
        mock_tf.GradientTape.return_value.__enter__.return_value = tape_nan

        with patch.dict('sys.modules', {'tensorflow': mock_tf}):
            heatmap = generator.compute_heatmap(np.zeros((1, 224, 224, 3)), mock_model, class_index=0)

            assert not np.isnan(heatmap).any(), "Heatmap must sanitize NaNs"
            assert np.all(heatmap == 0.0)

    def test_valid_gradcam_heatmap_computation(self):
        """Valid positive gradients must produce finite normalized heatmap in [0.0, 1.0]."""
        generator = GradCAMGenerator(layer_name='top_conv')
        mock_tf, mock_model = self._setup_mock_grad_model()

        grad_valid = np.ones((1, 7, 7, 16), dtype=np.float32)
        grad_valid[:, :3, :3, :] = 4.0
        tape_valid = MagicMock()
        tape_valid.gradient = MagicMock(return_value=MockTFTensor(grad_valid))
        mock_tf.GradientTape.return_value.__enter__.return_value = tape_valid

        with patch.dict('sys.modules', {'tensorflow': mock_tf}):
            heatmap = generator.compute_heatmap(np.zeros((1, 224, 224, 3)), mock_model, class_index=0)

            assert heatmap.shape == (7, 7)
            assert not np.isnan(heatmap).any()
            assert not np.isinf(heatmap).any()
            assert np.isclose(np.max(heatmap), 1.0)
            assert np.min(heatmap) >= 0.0

    def test_overlay_heatmap_dimensions_match_original(self):
        """Overlay dimensions must strictly match the original image dimensions."""
        generator = GradCAMGenerator(alpha=0.4)
        original_image = np.zeros((480, 640, 3), dtype=np.uint8)
        heatmap = np.random.uniform(0.0, 1.0, (7, 7)).astype(np.float32)

        overlay = generator.overlay_heatmap(original_image, heatmap)

        assert overlay.shape == (480, 640, 3), f"Overlay shape {overlay.shape} must match original (480, 640, 3)"
        assert overlay.dtype == np.uint8

    def test_overlay_heatmap_invalid_inputs(self):
        """Invalid or empty images/heatmaps must raise ValueError."""
        generator = GradCAMGenerator()
        with pytest.raises(ValueError):
            generator.overlay_heatmap(None, np.zeros((7, 7)))

        with pytest.raises(ValueError):
            generator.overlay_heatmap(np.zeros((10, 10, 3)), np.zeros((7, 7, 7, 7)))

    def test_remote_gradcam_base64_preservation(self, tmp_path):
        """Remote base64 heatmap must be preserved and written to disk without local model."""
        import cv2
        import base64
        dummy_overlay = np.zeros((224, 224, 3), dtype=np.uint8)
        dummy_overlay[:, :, 2] = 200  # Red highlight
        _, buf = cv2.imencode('.jpg', dummy_overlay)
        b64_str = base64.b64encode(buf).decode('utf-8')

        generator = GradCAMGenerator(output_dir=str(tmp_path))
        dummy_img = str(tmp_path / "sample.jpg")
        cv2.imwrite(dummy_img, np.zeros((224, 224, 3), dtype=np.uint8))

        saved_path = generator.generate(
            dummy_img,
            model=None,
            predicted_class_index=0,
            last_prediction_result={'heatmap_base64': b64_str}
        )

        assert os.path.exists(saved_path)
        saved_img = cv2.imread(saved_path)
        assert saved_img.shape == (224, 224, 3)

    def test_remote_gradcam_corrupted_base64_rejected(self, tmp_path):
        """Corrupted remote base64 strings or non-image payloads must be rejected."""
        import cv2
        import base64
        generator = GradCAMGenerator(output_dir=str(tmp_path))
        dummy_img = str(tmp_path / "sample.jpg")
        cv2.imwrite(dummy_img, np.zeros((224, 224, 3), dtype=np.uint8))

        # 1. Invalid base64 encoding
        with pytest.raises(ValueError, match="Invalid Base64 encoding|Remote heatmap"):
            generator.generate(
                dummy_img,
                model=None,
                predicted_class_index=0,
                last_prediction_result={'heatmap_base64': 'invalid_base64!@#$'}
            )

        # 2. Valid base64, but corrupted bytes that cannot be decoded as an image
        fake_b64 = base64.b64encode(b"corrupted_non_image_bytes").decode('utf-8')
        with pytest.raises(ValueError, match="Remote heatmap Base64 does not contain a valid, decodable image"):
            generator.generate(
                dummy_img,
                model=None,
                predicted_class_index=0,
                last_prediction_result={'heatmap_base64': fake_b64}
            )

    def test_gradcam_without_model_or_remote_raises_error(self, tmp_path):
        """Grad-CAM must fail with InferenceError if model is not loaded and no remote heatmap exists."""
        gradcam = GradCAMGenerator(output_dir=str(tmp_path))
        dummy_image = str(tmp_path / "test.jpg")

        # Create a small valid H&E stained test image file
        import cv2
        img = np.zeros((224, 224, 3), dtype=np.uint8)
        img[:, :, 0] = 160  # Blue
        img[:, :, 1] = 60   # Green
        img[:, :, 2] = 190  # Red
        cv2.circle(img, (112, 112), 30, (120, 20, 100), -1)
        cv2.imwrite(dummy_image, img)

        with pytest.raises(InferenceError) as exc_info:
            gradcam.generate(dummy_image, model=None, last_prediction_result=None)

        assert "Grad-CAM explainability failed" in str(exc_info.value)

    @staticmethod
    def _setup_mock_grad_model():
        """Helper to create a mock TensorFlow environment for compute_heatmap testing."""
        mock_tf = MagicMock()
        mock_tf.newaxis = np.newaxis
        mock_tf.reduce_mean = lambda x, axis: MockTFTensor(np.mean(x.val if isinstance(x, MockTFTensor) else x, axis=axis))
        mock_tf.math.is_nan = lambda x: MockTFTensor(np.isnan(x.val if isinstance(x, MockTFTensor) else x))
        mock_tf.math.is_inf = lambda x: MockTFTensor(np.isinf(x.val if isinstance(x, MockTFTensor) else x))
        mock_tf.math.reduce_max = lambda x: MockTFTensor(np.max(x.val if isinstance(x, MockTFTensor) else x))
        mock_tf.maximum = lambda x, y: MockTFTensor(np.maximum(x.val if isinstance(x, MockTFTensor) else x, y))
        mock_tf.squeeze = lambda x: MockTFTensor(np.squeeze(x.val if isinstance(x, MockTFTensor) else x))
        mock_tf.zeros_like = lambda x: MockTFTensor(np.zeros_like(x.val if isinstance(x, MockTFTensor) else x))
        mock_tf.where = lambda cond, x, y: MockTFTensor(np.where(cond.val if isinstance(cond, MockTFTensor) else cond, x.val if isinstance(x, MockTFTensor) else x, y.val if isinstance(y, MockTFTensor) else y))

        mock_sub_model = MagicMock()
        mock_target_layer = MagicMock()
        mock_target_layer.name = 'top_conv'
        mock_sub_model.get_layer = MagicMock(return_value=mock_target_layer)
        mock_sub_model.inputs = [MagicMock()]
        mock_sub_model.output = MagicMock()

        pred_arr = np.array([[0.8, 0.2]], dtype=np.float32)
        mock_dense = MagicMock(return_value=MockTFTensor(pred_arr))

        mock_model = MagicMock()
        mock_model.get_layer = MagicMock(side_effect=ValueError('No layer in root'))
        mock_model.layers = [mock_sub_model, mock_dense]

        conv_arr = np.ones((1, 7, 7, 16), dtype=np.float32) * 2.0
        mock_grad_model_instance = MagicMock(return_value=(MockTFTensor(conv_arr), MockTFTensor(pred_arr)))
        mock_tf.keras.models.Model.return_value = mock_grad_model_instance
        return mock_tf, mock_model


class MockTFTensor:
    """Helper tensor representation for testing gradient calculations without TensorFlow native DLLs."""
    def __init__(self, val):
        self.val = np.array(val, dtype=np.float32)
    @property
    def shape(self):
        return self.val.shape
    def numpy(self):
        return self.val
    def __matmul__(self, other):
        return MockTFTensor(np.matmul(self.val, other.val))
    def __getitem__(self, item):
        return MockTFTensor(self.val[item])
    def __truediv__(self, other):
        other_val = other.val if isinstance(other, MockTFTensor) else other
        return MockTFTensor(self.val / other_val)
    def __float__(self):
        return float(self.val)
