"""
ColonSightAI — Prediction Blueprint
======================================

Handles the AI prediction pipeline:
    - Image upload with validation
    - Run EfficientNetB0 inference
    - Display prediction results with confidence scores
    - Grad-CAM heatmap visualization
    - Prediction history and comparison
"""

from flask import Blueprint

prediction_bp = Blueprint(
    'prediction',
    __name__,
    template_folder='../../templates/prediction',
)

from app.blueprints.prediction import routes  # noqa: E402, F401
