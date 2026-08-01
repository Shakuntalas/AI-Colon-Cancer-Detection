"""
ColonSightAI — Configuration Tests
=====================================

Tests to verify that application configuration loads correctly
for all environments.
"""

from app import create_app
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig


class TestDevelopmentConfig:
    """Test development configuration."""

    def test_debug_is_true(self):
        """Development config should enable debug mode."""
        app = create_app('development')
        assert app.config['DEBUG'] is True

    def test_testing_is_false(self):
        """Development config should not enable testing mode."""
        app = create_app('development')
        assert app.config['TESTING'] is False


class TestTestingConfig:
    """Test testing configuration."""

    def test_testing_is_true(self):
        """Testing config should enable testing mode."""
        app = create_app('testing')
        assert app.config['TESTING'] is True

    def test_uses_memory_database(self):
        """Testing config should use in-memory SQLite."""
        app = create_app('testing')
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'

    def test_csrf_disabled(self):
        """Testing config should disable CSRF for easier testing."""
        app = create_app('testing')
        assert app.config['WTF_CSRF_ENABLED'] is False


class TestProductionConfig:
    """Test production configuration."""

    def test_debug_is_false(self):
        """Production config should disable debug mode."""
        app = create_app('production')
        assert app.config['DEBUG'] is False

    def test_testing_is_false(self):
        """Production config should disable testing mode."""
        app = create_app('production')
        assert app.config['TESTING'] is False
