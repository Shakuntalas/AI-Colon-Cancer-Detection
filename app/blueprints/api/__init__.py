"""
ColonSightAI — API Blueprint (v1)
====================================

RESTful API endpoints for programmatic access to ColonSightAI.

All endpoints are prefixed with ``/api/v1/`` and return JSON responses.

This blueprint enables:
    - Third-party integrations (LIMS, EMR systems)
    - Mobile application backends
    - Automated batch prediction pipelines
"""

from flask import Blueprint

api_bp = Blueprint(
    'api',
    __name__,
)

from app.blueprints.api import routes  # noqa: E402, F401
