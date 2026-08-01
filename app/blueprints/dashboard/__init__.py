"""
ColonSightAI — Dashboard Blueprint
=====================================

Handles the authenticated user's dashboard:
    - Overview with recent predictions and statistics
    - Prediction history timeline
    - Quick-access cards for common actions
"""

from flask import Blueprint

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='../../templates/dashboard',
)

from app.blueprints.dashboard import routes  # noqa: E402, F401
