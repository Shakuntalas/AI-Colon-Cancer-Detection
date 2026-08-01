"""
ColonSightAI — Blueprint Registry
===================================

This package houses all Flask Blueprints. Each sub-package is a
self-contained feature module with its own ``__init__.py`` (Blueprint
creation) and ``routes.py`` (route handlers).

Blueprints registered:
    ==================  ================  =====================================
    Blueprint           URL Prefix        Purpose
    ==================  ================  =====================================
    main_bp             /                 Landing, about, technology, errors
    auth_bp             /auth             Login, register, logout, forgot pw
    dashboard_bp        /dashboard        User dashboard & statistics
    patient_bp          /patient          Patient record management
    prediction_bp       /prediction       Image upload, inference, GradCAM
    report_bp           /report           PDF report generation & download
    admin_bp            /admin            Admin dashboard & user management
    api_bp              /api/v1           RESTful API endpoints
    ==================  ================  =====================================
"""
