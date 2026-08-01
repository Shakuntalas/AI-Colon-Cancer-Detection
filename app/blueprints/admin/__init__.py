"""
ColonSightAI — Admin Blueprint
=================================

Handles administrative functionality:
    - Admin dashboard with system-wide metrics
    - User management (view, activate, deactivate, role assignment)
    - System health monitoring
    - Model performance metrics
    - Audit logs
"""

from flask import Blueprint

admin_bp = Blueprint(
    'admin',
    __name__,
    template_folder='../../templates/admin',
)

from app.blueprints.admin import routes  # noqa: E402, F401
