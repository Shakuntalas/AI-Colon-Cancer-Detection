"""
ColonSightAI — Report Blueprint Routes
========================================

Route handlers for PDF report generation and management.

Routes:
    POST /report/generate/<prediction_id>    Generate a PDF report
    GET  /report/download/<report_id>        Download a generated report
    GET  /report/history                     View report history
    POST /report/<report_id>/delete          Delete a report
"""

from flask import render_template
from flask_login import login_required
from app.blueprints.report import report_bp


@report_bp.route('/generate/<int:prediction_id>', methods=['POST'])
@login_required
def generate(prediction_id):
    from flask import redirect, url_for
    return redirect(url_for('report.history'))


@report_bp.route('/download/<int:report_id>')
@login_required
def download(report_id):
    """Serve a generated PDF report for download."""
    return {
        'status': 'ok',
        'page': 'report_download',
        'id': report_id,
    }, 200


@report_bp.route('/history')
@login_required
def history():
    """Render the report history page with download links."""
    return render_template('report/history.html')


@report_bp.route('/<int:report_id>/delete', methods=['POST'])
@login_required
def delete(report_id):
    """Delete a generated report and its file."""
    from flask import redirect, url_for
    return redirect(url_for('report.history'))
