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

from app.blueprints.main import main_bp


@main_bp.route('/')
def landing():
    """Render the landing page with hero, features, workflow, and stats."""
    # TODO: Implement landing page template
    return {'status': 'ok', 'page': 'landing'}, 200


@main_bp.route('/about')
def about():
    """Render the About page with project details and team info."""
    # TODO: Implement about page template
    return {'status': 'ok', 'page': 'about'}, 200


@main_bp.route('/technology')
def technology():
    """Render the Technology page with stack details."""
    # TODO: Implement technology page template
    return {'status': 'ok', 'page': 'technology'}, 200


@main_bp.route('/workflow')
def workflow():
    """Render the AI Workflow visualization page."""
    # TODO: Implement workflow page template
    return {'status': 'ok', 'page': 'workflow'}, 200


@main_bp.route('/dataset')
def dataset():
    """Render the Dataset Information page."""
    # TODO: Implement dataset page template
    return {'status': 'ok', 'page': 'dataset'}, 200


@main_bp.route('/research')
def research():
    """Render the Research Highlights page."""
    # TODO: Implement research page template
    return {'status': 'ok', 'page': 'research'}, 200
