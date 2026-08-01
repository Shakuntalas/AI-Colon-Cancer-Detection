"""
ColonSightAI — Flask Extension Singletons
===========================================

This module creates extension instances *without* binding them to an
application. They are later initialised inside the application factory
via ``init_extensions(app)``.

This pattern avoids circular imports and supports the Application Factory.

Extensions:
    - **db** : Flask-SQLAlchemy — ORM and database management
    - **migrate** : Flask-Migrate — Alembic-based schema migrations
    - **login_manager** : Flask-Login — User session management
    - **csrf** : Flask-WTF CSRFProtect — CSRF token protection
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# ── Extension instances (unbound) ─────────────────────────────────────────
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def init_extensions(app: Flask) -> None:
    """
    Bind all Flask extension instances to the application.

    Parameters
    ----------
    app : Flask
        The Flask application instance created by the factory.
    """
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ── Login Manager configuration ───────────────────────────────────
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'

    # ── User loader callback ──────────────────────────────────────────
    @login_manager.user_loader
    def load_user(user_id):
        """Load a user by their primary key."""
        from app.models.user import User
        return User.query.get(int(user_id))
