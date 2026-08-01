"""
ColonSightAI — Development Entry Point
=======================================

Run this file to start the Flask development server.

Usage:
    python run.py

Note:
    For production, use wsgi.py with Gunicorn or uWSGI.
"""

import os
from app import create_app

# ---------------------------------------------------------------------------
# Resolve configuration from environment variable, default to 'development'
# ---------------------------------------------------------------------------
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = config_name == 'development'

    print(f"""
    ====================================================
               ColonSightAI - Dev Server              
    ----------------------------------------------------
      Host   : {host:<38s} 
      Port   : {port:<38d} 
      Debug  : {str(debug):<38s} 
      Config : {config_name:<38s} 
    ====================================================
    """)

    app.run(host=host, port=port, debug=debug)
