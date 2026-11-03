"""
ColonSightAI — Application Configuration
==========================================

This module defines configuration classes for different environments.
Each class inherits from ``BaseConfig`` and overrides settings as needed.

Configuration is loaded in the application factory via:
    ``app.config.from_object(config_class)``

Environment variables take precedence over defaults via ``os.getenv()``.
"""

import os
from datetime import timedelta

# ── Project root (two levels up from this file) ───────────────────────────
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class BaseConfig:
    """
    Base configuration shared across all environments.

    Attributes
    ----------
    SECRET_KEY : str
        Cryptographic key for sessions and CSRF protection.
    SQLALCHEMY_DATABASE_URI : str
        SQLite database connection string.
    SQLALCHEMY_TRACK_MODIFICATIONS : bool
        Disable modification tracking to save memory.
    """

    # ── Security ──────────────────────────────────────────────────────
    SECRET_KEY = os.getenv(
        'SECRET_KEY', 'dev-secret-key-change-in-production'
    )

    # ── Database ──────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "data", "database", "colonsightai.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── File Upload ───────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
    HEATMAP_FOLDER = os.path.join(BASE_DIR, 'data', 'heatmaps')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'data', 'reports')
    MODEL_FOLDER = os.path.join(BASE_DIR, 'data', 'models')
    DATABASE_FOLDER = os.path.join(BASE_DIR, 'data', 'database')
    LOG_FOLDER = os.path.join(BASE_DIR, 'logs')

    MAX_CONTENT_LENGTH = int(
        os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16 MB
    )
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'}

    # ── AI Model ──────────────────────────────────────────────────────
    MODEL_PATH = os.path.join(BASE_DIR, 'trained_models', 'efficientnetb0_colon.h5')
    MODEL_IMAGE_SIZE = int(os.getenv('MODEL_IMAGE_SIZE', 224))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
    REMOTE_INFERENCE_URL = os.getenv('REMOTE_INFERENCE_URL', None)

    # ── Session / Cookie ──────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(
        seconds=int(os.getenv('REMEMBER_COOKIE_DURATION', 604800))
    )

    # ── Logging ───────────────────────────────────────────────────────
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'colonsightai.log')


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    SESSION_COOKIE_SECURE = False


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'WARNING'
    SESSION_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    """
    Production environment configuration.

    .. warning::
        ``SECRET_KEY`` **must** be set via the ``SECRET_KEY`` environment
        variable in production. The default value is insecure.
    """

    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'


# ── Configuration map ─────────────────────────────────────────────────────
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
