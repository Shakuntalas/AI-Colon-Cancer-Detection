"""
ColonSightAI — Patient Blueprint Routes
=========================================

Route handlers for patient record management.

Routes:
    GET      /patient/                Patient list with search & pagination
    GET/POST /patient/add             Create new patient
    GET      /patient/<id>            View patient details
    GET/POST /patient/<id>/edit       Edit patient information
    POST     /patient/<id>/delete     Delete patient record
"""

from app.blueprints.patient import patient_bp


@patient_bp.route('/')
def patient_list():
    """Render the patient list page with search and pagination."""
    # TODO: Implement patient listing with filters
    return {'status': 'ok', 'page': 'patient_list'}, 200


@patient_bp.route('/add', methods=['GET', 'POST'])
def add_patient():
    """Handle new patient creation."""
    # TODO: Implement patient form and database insertion
    return {'status': 'ok', 'page': 'add_patient'}, 200


@patient_bp.route('/<int:patient_id>')
def view_patient(patient_id):
    """Render patient details page."""
    # TODO: Query patient record and render detail template
    return {'status': 'ok', 'page': 'view_patient', 'id': patient_id}, 200


@patient_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """Handle patient information update."""
    # TODO: Implement edit form with pre-populated data
    return {'status': 'ok', 'page': 'edit_patient', 'id': patient_id}, 200


@patient_bp.route('/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    """Handle patient record deletion."""
    # TODO: Implement soft delete with confirmation
    return {'status': 'ok', 'page': 'delete_patient', 'id': patient_id}, 200
