"""
ColonSightAI — Predictor
===========================

Runs genuine inference using the EfficientNetB0 colon cancer classification model
and returns structured prediction results.

Supports:
1. Genuine local inference via TensorFlow (when running in WSL2, Linux, or supported Windows environment).
2. Genuine remote inference via a dedicated inference microservice (Google Colab / Cloud Run)
   hosting the exact trained EfficientNetB0 model.

CRITICAL:
This module NEVER fabricates predictions, confidences, or probabilities.
If genuine inference cannot be executed, an InferenceError is raised.
"""

import os
import time
import logging
import requests

from app.ai.model_config import (
    CLASS_LABELS,
    CLASS_DISPLAY_NAMES,
    HIGH_CONFIDENCE,
    LOW_CONFIDENCE,
    MODEL_VERSION,
)

logger = logging.getLogger(__name__)


class InferenceError(RuntimeError):
    """Raised when genuine model inference cannot be performed (locally or remotely)."""
    pass


class Predictor:
    """
    EfficientNetB0 inference engine.

    Executes genuine predictions via a locally loaded TensorFlow model
    or a remote inference microservice (e.g. Google Colab / Cloud Run).
    """

    def predict(self, tensor, model=None, image_path=None):
        """
        Run genuine model inference on a preprocessed image tensor.

        Parameters
        ----------
        tensor : numpy.ndarray
            Preprocessed image tensor of shape (1, 224, 224, 3).
        model : tf.keras.Model, optional
            The loaded model. If None, attempts to load via ModelLoader.
        image_path : str, optional
            Path to the image file (used for remote inference).

        Returns
        -------
        dict
            Structured genuine prediction result:
                - predicted_class : str ('colon_aca' | 'colon_n')
                - display_name : str
                - confidence : float (0.0 – 1.0)
                - confidence_level : str ('high' | 'medium' | 'low')
                - all_probabilities : dict[str, float]
                - inference_time_ms : float
                - model_version : str

        Raises
        ------
        InferenceError
            If genuine model inference cannot be executed (e.g., local TensorFlow
            is blocked/unavailable and remote inference is not configured or failed).
        """
        remote_url = os.getenv('REMOTE_INFERENCE_URL')
        remote_error = None

        # 1. Attempt remote inference if configured
        if remote_url:
            try:
                return self._predict_remote(remote_url, tensor, image_path)
            except Exception as e:
                remote_error = e
                logger.error("Remote inference to %s failed: %s", remote_url, e)

        # 2. Attempt local model inference
        local_model = model
        local_error = None

        if local_model is None:
            try:
                from app.ai.model_loader import ModelLoader
                loader = ModelLoader()
                local_model = loader.get_model()
                if local_model is None and loader.get_load_error():
                    local_error = loader.get_load_error()
            except Exception as e:
                local_error = e

        if local_model is not None:
            return self._predict_local(local_model, tensor)

        # 3. If both remote and local fail or are unavailable, raise a clear InferenceError.
        # NEVER fabricate artificial predictions, color heuristics, or simulated confidences.
        err_msg_parts = []
        if remote_url:
            err_msg_parts.append(f"Remote inference to '{remote_url}' failed ({remote_error}).")
        else:
            err_msg_parts.append("No remote inference endpoint (REMOTE_INFERENCE_URL) is configured.")

        if local_error:
            err_msg_parts.append(f"Local TensorFlow model could not be loaded: {local_error}.")
        else:
            err_msg_parts.append("Local TensorFlow model is not loaded.")

        err_msg_parts.append(
            "Genuine inference is unavailable. Please ensure REMOTE_INFERENCE_URL is configured "
            "with a running Colab/cloud inference service or run the application in an environment "
            "with working TensorFlow (WSL2 / Linux)."
        )

        full_err_msg = " ".join(err_msg_parts)
        logger.error("Inference aborted: %s", full_err_msg)
        raise InferenceError(full_err_msg)

    def _predict_local(self, model, tensor):
        """Execute genuine inference on locally loaded Keras EfficientNetB0 model."""
        start_time = time.perf_counter()
        predictions = model.predict(tensor, verbose=0)
        inference_time = (time.perf_counter() - start_time) * 1000

        predicted_index = int(predictions[0].argmax())
        confidence = float(predictions[0][predicted_index])
        predicted_class = CLASS_LABELS[predicted_index]

        result = {
            'predicted_class': predicted_class,
            'display_name': CLASS_DISPLAY_NAMES[predicted_class],
            'confidence': round(confidence, 4),
            'confidence_level': self.interpret_confidence(confidence),
            'all_probabilities': {
                CLASS_LABELS[i]: round(float(p), 4)
                for i, p in enumerate(predictions[0])
            },
            'inference_time_ms': round(inference_time, 2),
            'model_version': MODEL_VERSION,
        }

        logger.info(
            'Genuine Local Inference: %s (%.2f%%) in %.1fms',
            result['display_name'],
            confidence * 100,
            inference_time,
        )
        return result

    def _predict_remote(self, url, tensor, image_path=None):
        """
        Forward image to remote Colab/Cloud inference endpoint running the trained model.
        Validates that genuine model output is returned.
        """
        start_time = time.perf_counter()

        try:
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    resp = requests.post(url, files={'file': f}, timeout=30)
            else:
                import json
                resp = requests.post(
                    url,
                    data=json.dumps({'tensor': tensor.tolist()}),
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            raise InferenceError(f"Remote inference connection to '{url}' failed: {e}") from e

        # Validate that the response contains genuine model prediction fields
        required_keys = ['predicted_class', 'confidence', 'all_probabilities']
        for k in required_keys:
            if k not in data:
                raise InferenceError(f"Remote inference returned invalid schema: missing key '{k}'")

        if data['predicted_class'] not in CLASS_LABELS.values():
            raise InferenceError(f"Remote inference returned unrecognized class: '{data['predicted_class']}'")

        # Validate probabilities structure
        probs = data['all_probabilities']
        if not isinstance(probs, dict) or not any(k in probs for k in CLASS_LABELS.values()):
            raise InferenceError("Remote inference returned malformed probability distribution")

        # Validate remote heatmap Base64 if provided
        if 'heatmap_base64' in data and data['heatmap_base64'] is not None:
            import base64
            import cv2
            import numpy as np
            try:
                raw_bytes = base64.b64decode(data['heatmap_base64'], validate=True)
                np_arr = np.frombuffer(raw_bytes, np.uint8)
                decoded_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if decoded_img is None or decoded_img.size == 0:
                    raise InferenceError("Remote inference returned invalid or corrupted heatmap image data")
            except Exception as e:
                if isinstance(e, InferenceError):
                    raise
                raise InferenceError(f"Remote inference returned corrupted heatmap Base64: {e}") from e

        data['confidence'] = float(data['confidence'])
        data['confidence_level'] = self.interpret_confidence(data['confidence'])
        data['display_name'] = CLASS_DISPLAY_NAMES.get(data['predicted_class'], data['predicted_class'])
        data['inference_time_ms'] = round((time.perf_counter() - start_time) * 1000, 2)
        data['model_version'] = data.get('model_version', MODEL_VERSION)

        logger.info(
            'Genuine Remote Inference received: %s (%.2f%%) in %.1fms',
            data['display_name'],
            data['confidence'] * 100,
            data['inference_time_ms'],
        )
        return data

    @staticmethod
    def interpret_confidence(confidence):
        """
        Map a confidence score to a human-readable level.

        Parameters
        ----------
        confidence : float
            Model confidence score (0.0 – 1.0).

        Returns
        -------
        str
            One of: 'high', 'medium', 'low'.
        """
        if confidence >= HIGH_CONFIDENCE:
            return 'high'
        elif confidence >= LOW_CONFIDENCE:
            return 'medium'
        return 'low'
