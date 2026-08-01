"""
ColonSightAI — Models Package
===============================

Exposes all SQLAlchemy models for easy importing and Alembic migrations.
"""

from app.models.user import User
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.admin import Admin
from app.models.history import History

__all__ = [
    'User',
    'Patient',
    'Prediction',
    'Admin',
    'History',
]
