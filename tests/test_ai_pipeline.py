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
from app.ai.predictor import Predictor


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
        """All class indices should have labels."""
        assert 0 in CLASS_LABELS
        assert 1 in CLASS_LABELS

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
