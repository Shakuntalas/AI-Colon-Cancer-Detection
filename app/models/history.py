"""
ColonSightAI — History Model
===============================

Defines the History database model for audit logs and user activity tracking.
"""

from app.extensions import db
from datetime import datetime, timezone


class History(db.Model):
    """System audit log and user activity history model."""

    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<History {self.action} by User {self.user_id}>'
