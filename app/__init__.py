"""
ColonSightAI — Application Factory
====================================

This module implements the Flask Application Factory pattern, providing
a ``create_app`` callable that constructs and configures the Flask
application instance.

Architecture:
    1. Load configuration from the appropriate config class.
    2. Initialize Flask extensions (database, login manager, CSRF, etc.).
    3. Register all Blueprints (auth, main, dashboard, patient, prediction,
       report, admin, api).
    4. Configure logging with structured output to file and console.
    5. Ensure runtime directories (uploads, heatmaps, reports, logs) exist.
    6. Register global error handlers.

Usage:
    from app import create_app
    app = create_app('development')
"""

import os
import logging
from flask import Flask

from app.config import config_map
from app.extensions import init_extensions
from app.utils.logger import setup_logging


def create_app(config_name: str = 'development') -> Flask:
    """
    Create and configure the Flask application.

    Parameters
    ----------
    config_name : str
        Configuration profile to load. One of:
        ``'development'``, ``'testing'``, ``'production'``.

    Returns
    -------
    Flask
        The configured Flask application instance.
    """
    # ── Create Flask instance ──────────────────────────────────────────
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates',
    )

    # ── Load configuration ─────────────────────────────────────────────
    config_class = config_map.get(config_name, config_map['development'])
    app.config.from_object(config_class)

    # ── Initialise extensions ──────────────────────────────────────────
    init_extensions(app)

    # ── Configure logging ──────────────────────────────────────────────
    setup_logging(app)

    # ── Ensure runtime directories exist ───────────────────────────────
    _ensure_directories(app)

    # ── Register middleware ────────────────────────────────────────────
    from app.middleware import register_middleware
    register_middleware(app)

    # ── Register blueprints ────────────────────────────────────────────
    _register_blueprints(app)

    # ── Register error handlers ────────────────────────────────────────
    _register_error_handlers(app)

    app.logger.info(
        'ColonSightAI application created [config=%s]', config_name
    )
    return app


# ═══════════════════════════════════════════════════════════════════════════
# Private helpers
# ═══════════════════════════════════════════════════════════════════════════

def _register_blueprints(app: Flask) -> None:
    """Import and register all application blueprints."""
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.patient import patient_bp
    from app.blueprints.prediction import prediction_bp
    from app.blueprints.report import report_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(prediction_bp, url_prefix='/prediction')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api/v1')


def _register_error_handlers(app: Flask) -> None:
    """Register global HTTP error handlers."""

    @app.errorhandler(401)
    def unauthorized(error):  # noqa: F841
        return {'error': 'Unauthorized access'}, 401

    @app.errorhandler(403)
    def forbidden(error):  # noqa: F841
        return {'error': 'Forbidden access'}, 403

    @app.errorhandler(404)
    def page_not_found(error):  # noqa: F841
        return {'error': 'Page not found'}, 404

    @app.errorhandler(500)
    def internal_server_error(error):  # noqa: F841
        app.logger.error('Internal server error: %s', error)
        return {'error': 'Internal server error'}, 500

    @app.errorhandler(413)
    def request_entity_too_large(error):  # noqa: F841
        return {'error': 'File too large'}, 413


def _ensure_directories(app: Flask) -> None:
    """Create runtime directories if they do not exist."""
    directories = [
        app.config.get('UPLOAD_FOLDER', 'data/uploads'),
        app.config.get('HEATMAP_FOLDER', 'data/heatmaps'),
        app.config.get('REPORT_FOLDER', 'data/reports'),
        app.config.get('MODEL_FOLDER', 'data/models'),
        app.config.get('DATABASE_FOLDER', 'data/database'),
        app.config.get('LOG_FOLDER', 'logs'),
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
