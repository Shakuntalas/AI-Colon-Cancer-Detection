"""
ColonSightAI — Prediction Model
==================================

Defines the Prediction database model for storing AI inference results.

Table: ``predictions``

Fields:
    id                  : int (PK, auto-increment)
    prediction_uid      : str (unique, system-generated)
    patient_id          : int (FK → patients.id, nullable)
    user_id             : int (FK → users.id, not null)
    original_image_path : str (not null) — path to uploaded histopathology image
    heatmap_image_path  : str — path to Grad-CAM heatmap overlay
    predicted_class     : str — 'colon_aca' | 'colon_n' (adenocarcinoma / normal)
    confidence_score    : float — model confidence (0.0 – 1.0)
    model_version       : str — version of the model used
    preprocessing_info  : text (JSON) — preprocessing steps applied
    inference_time_ms   : float — inference duration in milliseconds
    report_path         : str — path to generated PDF report
    status              : str — 'pending' | 'completed' | 'failed'
    notes               : text — clinician annotations
    created_at          : datetime (auto)

Relationships:
    - Many-to-One with User
    - Many-to-One with Patient (optional)
"""

from app.extensions import db
from datetime import datetime, timezone


class Prediction(db.Model):
    """AI prediction result model."""

    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prediction_uid = db.Column(db.String(40), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_image_path = db.Column(db.String(512), nullable=False)
    heatmap_image_path = db.Column(db.String(512))
    predicted_class = db.Column(db.String(20))
    confidence_score = db.Column(db.Float)
    model_version = db.Column(db.String(20))
    preprocessing_info = db.Column(db.Text)
    inference_time_ms = db.Column(db.Float)
    report_path = db.Column(db.String(512))
    status = db.Column(db.String(20), default='pending', nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Prediction {self.prediction_uid} — {self.predicted_class}>'
