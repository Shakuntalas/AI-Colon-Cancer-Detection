"""
ColonSightAI — Application Middleware
=======================================

Defines custom request/response middleware for the Flask application.
"""

from flask import request, g
import time


def register_middleware(app):
    """
    Register all middleware functions with the application.
    """

    @app.before_request
    def start_timer():
        """Start a timer to measure request duration."""
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        """Log request details and execution time, and add security headers."""
        # Calculate duration
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.debug(
                f"[{request.method}] {request.path} - Status: {response.status_code} "
                f"- Duration: {duration:.4f}s"
            )

        # Add generic security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
