# 🏗️ App — Flask Application Package

## Purpose

This is the core Flask application package. It contains the application factory, configuration, extensions, blueprints, models, services, AI pipeline, utilities, static assets, and templates.

## Structure

```
app/
├── __init__.py         ← Application factory (create_app)
├── config.py           ← Configuration classes (Dev/Test/Prod)
├── extensions.py       ← Flask extension singletons
├── blueprints/         ← 8 modular route blueprints
├── models/             ← SQLAlchemy ORM models
├── services/           ← Business logic layer
├── ai/                 ← Deep learning pipeline
├── utils/              ← Shared utilities
├── static/             ← CSS, JS, images, vendor libs
└── templates/          ← Jinja2 HTML templates
```

## Application Factory Pattern

The `create_app()` function in `__init__.py` builds the Flask app by:
1. Loading the appropriate configuration class
2. Initializing Flask extensions (SQLAlchemy, Migrate, Login, CSRF)
3. Registering all 8 Blueprints with URL prefixes
4. Configuring structured logging
5. Ensuring runtime directories exist
6. Registering global error handlers
