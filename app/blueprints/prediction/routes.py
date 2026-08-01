"""
ColonSightAI — Prediction Blueprint Routes
============================================

Route handlers for the AI prediction pipeline.

Routes:
    GET      /prediction/                Prediction landing / upload form
    POST     /prediction/upload          Process uploaded histopathology image
    GET      /prediction/<id>/result     View prediction result
    GET      /prediction/<id>/gradcam    View Grad-CAM heatmap overlay
    GET      /prediction/history         Prediction history for current user
    POST     /prediction/<id>/delete     Delete a prediction record
"""

from flask import render_template
from flask_login import login_required
from app.blueprints.prediction import prediction_bp


@prediction_bp.route('/')
@login_required
def index():
    """Render the prediction upload form."""
    return render_template('prediction/index.html')


@prediction_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    from flask import redirect, url_for
    return redirect(url_for('prediction.result', prediction_id=1))


@prediction_bp.route('/<int:prediction_id>/result')
@login_required
def result(prediction_id):
    """Display prediction result with confidence score and classification."""
    return render_template('prediction/result.html', prediction_id=prediction_id)


@prediction_bp.route('/<int:prediction_id>/gradcam')
@login_required
def gradcam(prediction_id):
    """Display the Grad-CAM heatmap overlay for explainability."""
    return render_template('prediction/gradcam.html', prediction_id=prediction_id)


@prediction_bp.route('/history')
@login_required
def history():
    """Render paginated prediction history for the logged-in user."""
    return render_template('prediction/history.html')


@prediction_bp.route('/<int:prediction_id>/delete', methods=['POST'])
@login_required
def delete(prediction_id):
    """Delete a prediction record and associated files."""
    from flask import redirect, url_for
    return redirect(url_for('prediction.history'))
