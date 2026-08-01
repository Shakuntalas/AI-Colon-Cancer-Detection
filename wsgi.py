"""
ColonSightAI — Production WSGI Entry Point
============================================

This module exposes the Flask application for production WSGI servers.

Usage with Gunicorn:
    gunicorn wsgi:app --workers 4 --bind 0.0.0.0:8000

Usage with uWSGI:
    uwsgi --http :8000 --module wsgi:app --processes 4
"""

import os
from app import create_app

config_name = os.getenv('FLASK_CONFIG', 'production')
app = create_app(config_name)
