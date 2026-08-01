"""
ColonSightAI — User Model
============================

Defines the User database model for authentication and authorization.

Table: ``users``

Fields:
    id              : int (PK, auto-increment)
    username        : str (unique, indexed, not null)
    email           : str (unique, indexed, not null)
    password_hash   : str (not null)
    first_name      : str
    last_name       : str
    role            : str (default 'clinician') — clinician | admin | researcher
    is_active       : bool (default True)
    created_at      : datetime (auto)
    updated_at      : datetime (auto)
    last_login      : datetime

Relationships:
    - One-to-Many with Prediction
"""

# TODO: Implement User model
#
# from app.extensions import db
# from flask_login import UserMixin
# from datetime import datetime, timezone
#
#
# class User(UserMixin, db.Model):
#     \"\"\"User account model.\"\"\"
#
#     __tablename__ = 'users'
#
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(120), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(256), nullable=False)
#     first_name = db.Column(db.String(80))
#     last_name = db.Column(db.String(80))
#     role = db.Column(db.String(20), default='clinician', nullable=False)
#     is_active = db.Column(db.Boolean, default=True, nullable=False)
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     updated_at = db.Column(
#         db.DateTime,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )
#     last_login = db.Column(db.DateTime)
#
#     # ── Relationships ─────────────────────────────────────────────────
#     predictions = db.relationship('Prediction', backref='user', lazy='dynamic')
#
#     def __repr__(self):
#         return f'<User {self.username}>'
