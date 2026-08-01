"""
ColonSightAI — Patient Blueprint
==================================

Handles patient record management:
    - Create new patient records
    - View patient details
    - Update patient information
    - List all patients with search and filters
    - Delete patient records
"""

from flask import Blueprint

patient_bp = Blueprint(
    'patient',
    __name__,
    template_folder='../../templates/patient',
)

from app.blueprints.patient import routes  # noqa: E402, F401
