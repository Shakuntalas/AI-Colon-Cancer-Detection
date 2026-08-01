"""
ColonSightAI — Report Blueprint
==================================

Handles PDF report generation and management:
    - Generate diagnostic PDF reports with ReportLab
    - Download generated reports
    - View report history
"""

from flask import Blueprint

report_bp = Blueprint(
    'report',
    __name__,
    template_folder='../../templates/report',
)

from app.blueprints.report import routes  # noqa: E402, F401
