"""
ColonSightAI — Dashboard Blueprint Routes
===========================================

Route handlers for the authenticated user dashboard.

Routes:
    GET /dashboard/            Dashboard overview
    GET /dashboard/stats       Prediction statistics (AJAX)
    GET /dashboard/history     Full prediction history
    GET /dashboard/settings    User settings
    GET /dashboard/profile     User profile
"""

from flask import render_template
from app.blueprints.dashboard import dashboard_bp


@dashboard_bp.route('/')
def index():
    """Render the main dashboard with overview cards and recent activity."""
    return render_template('dashboard/index.html')


@dashboard_bp.route('/stats')
def stats():
    """Return dashboard statistics (for AJAX chart rendering)."""
    return {'status': 'ok', 'page': 'dashboard_stats'}, 200


@dashboard_bp.route('/history')
def history():
    """Render full prediction history with filters and pagination."""
    return render_template('dashboard/history.html')


@dashboard_bp.route('/settings')
def settings():
    """Render user settings page."""
    return render_template('dashboard/settings.html')


@dashboard_bp.route('/profile')
def profile():
    """Render user profile page."""
    return render_template('dashboard/profile.html')
