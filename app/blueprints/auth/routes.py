"""
ColonSightAI — Auth Blueprint Routes
======================================

Route handlers for authentication flows.

Routes:
    GET/POST /auth/login             User login
    GET/POST /auth/register          User registration
    GET      /auth/logout            User logout
    GET/POST /auth/forgot-password   Password reset request
    GET/POST /auth/reset-password    Password reset confirmation
"""

from flask import render_template
from app.blueprints.auth import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration."""
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """Log out the current user and redirect to landing."""
    # Redirect to landing for now
    from flask import redirect, url_for
    return redirect(url_for('main.landing'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request."""
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with a valid token."""
    return render_template('auth/reset_password.html', token=token)
