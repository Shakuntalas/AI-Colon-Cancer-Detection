"""
ColonSightAI — Custom Decorators
===================================

Reusable decorators for route protection, error handling,
and cross-cutting concerns.
"""

import functools
import logging
import time

from flask import abort, flash, redirect, url_for

logger = logging.getLogger(__name__)


def login_required(f):
    """
    Decorator to require authentication for a route.

    Redirects unauthenticated users to the login page with a flash message.

    Usage:
        @dashboard_bp.route('/protected')
        @login_required
        def protected_page():
            ...
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement with Flask-Login's current_user
        #
        # from flask_login import current_user
        # if not current_user.is_authenticated:
        #     flash('Please log in to access this page.', 'warning')
        #     return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role for a route.

    Returns 403 Forbidden if the current user is not an admin.

    Usage:
        @admin_bp.route('/admin-only')
        @login_required
        @admin_required
        def admin_page():
            ...
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: Implement with Flask-Login's current_user
        #
        # from flask_login import current_user
        # if not current_user.is_authenticated or current_user.role != 'admin':
        #     abort(403)
        return f(*args, **kwargs)
    return decorated_function


def handle_errors(f):
    """
    Decorator to catch and log exceptions in route handlers.

    Logs the full traceback and returns a generic error response.

    Usage:
        @prediction_bp.route('/predict', methods=['POST'])
        @handle_errors
        def predict():
            ...
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception('Unhandled error in %s: %s', f.__name__, e)
            return {
                'error': 'An unexpected error occurred. Please try again.'
            }, 500
    return decorated_function


def timing(f):
    """
    Decorator to log the execution time of a function.

    Usage:
        @timing
        def expensive_operation():
            ...
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start = time.perf_counter()
        result = f(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        logger.debug('%s executed in %.2fms', f.__name__, elapsed)
        return result
    return decorated_function
