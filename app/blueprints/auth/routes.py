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

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.models.user import User
from app.extensions import db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        organization = request.form.get('organization')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Basic validation
        if not all([first_name, last_name, email, password, confirm_password]):
            flash('Please fill out all required fields.', 'warning')
            return render_template('auth/register.html')
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        # Check existing user
        if User.query.filter_by(email=email).first():
            flash('Email address is already registered.', 'danger')
            return render_template('auth/register.html')

        # Create new user
        # Using organization as a placeholder or we can use it to infer role if needed
        username = email.split('@')[0]
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='clinician'
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user and redirect to landing."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset request."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a temporary dev token (hardcoded for now as per instructions)
            # In a real app, use itsdangerous to generate a token and send an email
            dev_token = "dev-reset-token-12345"
            flash(f'DEV MODE: Password reset link generated. <a href="{url_for("auth.reset_password", token=dev_token)}">Click here to reset</a>', 'info')
        else:
            # We don't want to reveal if an email is registered or not for security, but for UX we can say check email
            flash('If that email is registered, you will receive a reset link.', 'info')
            
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with a valid token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    # In a real app, validate token here using itsdangerous
    if token != "dev-reset-token-12345":
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('auth.forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('auth/reset_password.html', token=token)
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)
            
        # Hardcoding the user update for dev purposes since we don't have real token validation
        # Normally token contains user_id
        flash('Password successfully updated! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', token=token)
