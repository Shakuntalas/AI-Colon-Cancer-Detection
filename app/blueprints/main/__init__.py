"""
ColonSightAI — Main Blueprint
===============================

Handles public-facing pages that do not require authentication:
    - Landing page (hero, features, workflow, research, stats, footer)
    - About page
    - Technology page
    - AI Workflow page
    - Dataset information
    - Research section
"""

from flask import Blueprint

main_bp = Blueprint(
    'main',
    __name__,
    template_folder='../../templates/main',
    static_folder='../../static',
)

from app.blueprints.main import routes  # noqa: E402, F401
