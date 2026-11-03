"""
ColonSightAI — Model Loader
==============================

Handles loading and caching of the EfficientNetB0 model.

The model is loaded once at application startup and cached in memory
using a singleton pattern to avoid reloading on every prediction request.

Usage:
    from app.ai.model_loader import ModelLoader

    loader = ModelLoader()
    model = loader.get_model()
"""

import os
import logging

from app.ai.model_config import MODEL_PATH, MODEL_NAME, MODEL_VERSION

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Singleton model loader for the EfficientNetB0 colon cancer classifier.

    The model is loaded from disk on first access and cached for subsequent
    calls. Thread-safe via Flask's application context.

    Attributes
    ----------
    _model : tf.keras.Model or None
        The cached Keras model instance.
    _is_loaded : bool
        Whether the model has been successfully loaded.
    """

    _instance = None
    _model = None
    _is_loaded = False
    _load_error = None

    def __new__(cls):
        """Enforce singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_load_error(self):
        """Return the exception encountered when loading the model, if any."""
        return self._load_error

    def get_model(self):
        """
        Return the loaded Keras model, loading it from disk if necessary.

        Returns
        -------
        tf.keras.Model or None
            The loaded EfficientNetB0 model, or None if using remote inference.
        """
        if not self._is_loaded and self._load_error is None:
            self._load_model()
        return self._model

    def _load_model(self):
        """Load the model weights from disk or initialize remote inference."""
        remote_url = os.getenv('REMOTE_INFERENCE_URL')
        if remote_url:
            logger.info('Remote inference URL configured: %s. Local TensorFlow model loading skipped.', remote_url)
            self._is_loaded = True
            return

        if not os.path.exists(MODEL_PATH):
            err = FileNotFoundError(
                f'Model file not found: {MODEL_PATH}. '
                'Please train the model first using scripts/train_model.py'
            )
            self._load_error = err
            raise err

        logger.info('Loading %s model from %s ...', MODEL_NAME, MODEL_PATH)
        try:
            import tensorflow as tf
            self._model = tf.keras.models.load_model(MODEL_PATH)
            self._is_loaded = True
            logger.info(
                '%s v%s loaded successfully. '
                'Input shape: %s, Output classes: %s',
                MODEL_NAME, MODEL_VERSION,
                self._model.input_shape, self._model.output_shape,
            )
        except (ImportError, OSError) as err:
            self._load_error = err
            err_str = str(err)
            if 'Application Control policy' in err_str or '_pywrap_utils' in err_str:
                logger.error(
                    'Windows Code Integrity / Smart App Control blocked local TensorFlow (_pywrap_utils.pyd).\n'
                    'Policy ID: {0283AC0F-FFF1-49AE-ADA1-8A933130CAD6}\n'
                    'To run predictions: Configure REMOTE_INFERENCE_URL in .env (e.g. Google Colab) '
                    'or execute in WSL2 / Linux.'
                )
            else:
                logger.error('Failed to load TensorFlow locally: %s', err)

            if not remote_url:
                raise RuntimeError(
                    f'TensorFlow could not be loaded due to Windows Code Integrity Policy: {err}'
                ) from err

    def is_loaded(self):
        """Check if the model is currently loaded in memory."""
        return self._is_loaded

    def reload_model(self):
        """Force-reload the model from disk."""
        self._is_loaded = False
        self._model = None
        self._load_model()

    def get_model_info(self):
        """Return metadata about the loaded model."""
        return {
            'name': MODEL_NAME,
            'version': MODEL_VERSION,
            'path': MODEL_PATH,
            'is_loaded': self._is_loaded,
            'file_exists': os.path.exists(MODEL_PATH),
        }
