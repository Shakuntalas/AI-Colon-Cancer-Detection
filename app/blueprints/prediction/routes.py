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

from flask import render_template, request, current_app, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.prediction import prediction_bp
from app.extensions import db
from app.models.prediction import Prediction
import os
import uuid
from werkzeug.utils import secure_filename
import traceback

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@prediction_bp.route('/')
@login_required
def index():
    """Render the prediction upload form."""
    return render_template('prediction/index.html')


@prediction_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Process uploaded histopathology image."""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
        
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            unique_id = uuid.uuid4().hex[:8]
            ext = filename.rsplit('.', 1)[1].lower()
            save_name = f"{unique_id}.{ext}"
            
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, save_name)
            file.save(file_path)
            
            # Imports
            from app.ai.preprocessor import ImagePreprocessor
            from app.ai.predictor import Predictor
            from app.ai.gradcam import GradCAMGenerator
            from app.utils.report_generator import generate_pdf_report
            from app.ai.model_loader import ModelLoader
            
            # Inference
            preprocessor = ImagePreprocessor()
            tensor = preprocessor.preprocess(file_path)
            
            model = ModelLoader().get_model()
            predictor = Predictor()
            result = predictor.predict(tensor, model)
            
            # Grad-CAM
            gradcam_gen = GradCAMGenerator()
            # Predictor predicted index can be inferred from probability dict or just re-calculate
            predicted_index = 0 if result['predicted_class'] == 'colon_aca' else 1
            heatmap_path_abs = gradcam_gen.generate(file_path, model, predicted_index)
            
            # Report
            report_dir = current_app.config['REPORT_FOLDER']
            report_path_abs = generate_pdf_report(result, file_path, heatmap_path_abs, report_dir)
            
            # Database
            prediction = Prediction(
                prediction_uid=unique_id,
                user_id=current_user.id,
                original_image_path=file_path,
                heatmap_image_path=heatmap_path_abs,
                predicted_class=result['predicted_class'],
                confidence_score=result['confidence'],
                model_version=result['model_version'],
                inference_time_ms=result['inference_time_ms'],
                report_path=report_path_abs,
                status='completed'
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            return redirect(url_for('prediction.result', prediction_id=prediction.id))
            
        except Exception as e:
            current_app.logger.error(f"Prediction failed: {e}\n{traceback.format_exc()}")
            db.session.rollback()
            flash(f"An error occurred during prediction: {e}", 'danger')
            return redirect(url_for('prediction.index'))
            
    flash('Invalid file type. Allowed: PNG, JPG, JPEG, TIFF', 'warning')
    return redirect(url_for('prediction.index'))


@prediction_bp.route('/<int:prediction_id>/result')
@login_required
def result(prediction_id):
    """Display prediction result with confidence score and classification."""
    prediction = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first_or_404()
    return render_template('prediction/result.html', prediction=prediction)


@prediction_bp.route('/<int:prediction_id>/gradcam')
@login_required
def gradcam(prediction_id):
    """Display the Grad-CAM heatmap overlay for explainability."""
    prediction = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first_or_404()
    return render_template('prediction/gradcam.html', prediction=prediction)


@prediction_bp.route('/images/<filename>')
@login_required
def serve_image(filename):
    from flask import send_from_directory
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@prediction_bp.route('/heatmaps/<filename>')
@login_required
def serve_heatmap(filename):
    from flask import send_from_directory
    return send_from_directory(current_app.config['HEATMAP_FOLDER'], filename)


@prediction_bp.route('/<int:prediction_id>/report')
@login_required
def download_report(prediction_id):
    from flask import send_file
    prediction = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first_or_404()
    if prediction.report_path and os.path.exists(prediction.report_path):
        return send_file(prediction.report_path, as_attachment=True)
    flash("Report not found.", "danger")
    return redirect(url_for('prediction.result', prediction_id=prediction_id))

@prediction_bp.route('/history')
@login_required
def history():
    """Render paginated prediction history for the logged-in user."""
    page = request.args.get('page', 1, type=int)
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('prediction/history.html', predictions=predictions)


@prediction_bp.route('/<int:prediction_id>/delete', methods=['POST'])
@login_required
def delete(prediction_id):
    """Delete a prediction record and associated files."""
    prediction = Prediction.query.filter_by(id=prediction_id, user_id=current_user.id).first_or_404()
    
    # Delete files
    try:
        if prediction.original_image_path and os.path.exists(prediction.original_image_path):
            os.remove(prediction.original_image_path)
        if prediction.heatmap_image_path and os.path.exists(prediction.heatmap_image_path):
            os.remove(prediction.heatmap_image_path)
        if prediction.report_path and os.path.exists(prediction.report_path):
            os.remove(prediction.report_path)
    except Exception as e:
        current_app.logger.warning(f"Failed to delete files for prediction {prediction.id}: {e}")
        
    db.session.delete(prediction)
    db.session.commit()
    flash('Prediction record deleted successfully.', 'success')
    return redirect(url_for('prediction.history'))
