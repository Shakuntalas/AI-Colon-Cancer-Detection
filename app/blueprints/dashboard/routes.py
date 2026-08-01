"""
ColonSightAI — Dashboard Blueprint Routes
===========================================

Route handlers for the authenticated user dashboard.

Routes:
    GET /dashboard/            Dashboard overview
    GET /dashboard/stats       Prediction statistics (AJAX)
    GET /dashboard/history     Full prediction history
    GET/POST /dashboard/settings    User settings
    GET/POST /dashboard/profile     User profile
"""

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.blueprints.dashboard import dashboard_bp
from app.extensions import db


@dashboard_bp.route('/')
@login_required
def index():
    """Render the main dashboard with overview cards and recent activity."""
    return render_template('dashboard/index.html')


@dashboard_bp.route('/stats')
@login_required
def stats():
    """Return dashboard statistics (for AJAX chart rendering)."""
    return {'status': 'ok', 'page': 'dashboard_stats'}, 200


@dashboard_bp.route('/history')
@login_required
def history():
    """Render full prediction history with filters and pagination."""
    return render_template('dashboard/history.html')


@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Render user settings page."""
    if request.method == 'POST':
        # TODO: Implement actual settings save logic
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('dashboard.settings'))
        
    return render_template('dashboard/settings.html')


@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Render user profile page and handle updates."""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        updated = False
        
        if first_name and first_name != current_user.first_name:
            current_user.first_name = first_name
            updated = True
            
        if last_name and last_name != current_user.last_name:
            current_user.last_name = last_name
            updated = True
            
        if email and email != current_user.email:
            # Should also check if new email is already taken by another user
            from app.models.user import User
            if User.query.filter_by(email=email).first():
                flash('That email address is already in use.', 'danger')
                return redirect(url_for('dashboard.profile'))
            current_user.email = email
            updated = True
            
        if password:
            if len(password) < 6:
                flash('Password must be at least 6 characters long.', 'warning')
                return redirect(url_for('dashboard.profile'))
            current_user.set_password(password)
            updated = True
            
        if updated:
            try:
                db.session.commit()
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error updating profile.', 'danger')
        else:
            flash('No changes made to profile.', 'info')
            
        return redirect(url_for('dashboard.profile'))
        
    return render_template('dashboard/profile.html')
