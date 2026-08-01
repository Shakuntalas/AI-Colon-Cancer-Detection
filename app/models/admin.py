"""
ColonSightAI — Admin Model
=============================

Defines the Admin database model for system-wide configurations.
"""

from app.extensions import db
from datetime import datetime, timezone


class Admin(db.Model):
    """Admin configuration or privileged user details model."""

    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    department = db.Column(db.String(120))
    access_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relationships ─────────────────────────────────────────────────
    user = db.relationship('User', backref=db.backref('admin_profile', uselist=False))

    def __repr__(self):
        return f'<Admin Profile for User ID {self.user_id}>'
