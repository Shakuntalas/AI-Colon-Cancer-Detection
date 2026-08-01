"""
ColonSightAI — Main Blueprint Routes
======================================

Route handlers for public-facing pages.

Routes:
    GET /               Landing page
    GET /about           About ColonSightAI
    GET /technology      Technology stack & architecture
    GET /workflow        AI workflow visualization
    GET /dataset         Dataset information
    GET /research        Research highlights
"""

from flask import render_template
from app.blueprints.main import main_bp


@main_bp.route('/')
def landing():
    """Render the landing page with hero, features, workflow, and stats."""
    return render_template('main/landing.html')


@main_bp.route('/about')
def about():
    """Render the About page with project details and team info."""
    return render_template('main/about.html')


@main_bp.route('/technology')
def technology():
    """Render the Technology page with stack details."""
    return render_template('main/technology.html')


@main_bp.route('/workflow')
def workflow():
    """Render the AI Workflow visualization page."""
    return render_template('main/workflow.html')


@main_bp.route('/dataset')
def dataset():
    """Render the Dataset Information page."""
    return render_template('main/dataset.html')


@main_bp.route('/research')
def research():
    """Render the Research Highlights page."""
    return render_template('main/research.html')


@main_bp.route('/contact')
def contact():
    """Render the Contact page."""
    return render_template('main/contact.html')
