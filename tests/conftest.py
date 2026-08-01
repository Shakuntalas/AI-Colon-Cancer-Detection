"""
ColonSightAI — Pytest Fixtures
=================================

Shared test fixtures for the ColonSightAI test suite.

Fixtures:
    - ``app`` — Flask application configured for testing
    - ``client`` — Flask test client
    - ``runner`` — Flask CLI test runner
    - ``temp_upload_dir`` — Temporary upload directory
"""

import os
import tempfile

import pytest

from app import create_app


@pytest.fixture(scope='session')
def app():
    """
    Create a Flask application instance configured for testing.

    Yields the app instance for the entire test session.
    """
    app = create_app('testing')

    # Create a temporary directory for uploads during tests
    with tempfile.TemporaryDirectory() as tmpdir:
        app.config['UPLOAD_FOLDER'] = os.path.join(tmpdir, 'uploads')
        app.config['HEATMAP_FOLDER'] = os.path.join(tmpdir, 'heatmaps')
        app.config['REPORT_FOLDER'] = os.path.join(tmpdir, 'reports')

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['HEATMAP_FOLDER'], exist_ok=True)
        os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

        yield app


@pytest.fixture()
def client(app):
    """Create a Flask test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture()
def runner(app):
    """Create a Flask CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture()
def temp_upload_dir():
    """Create a temporary directory for file upload tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
