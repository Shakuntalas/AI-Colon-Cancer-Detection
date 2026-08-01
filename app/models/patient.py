"""
ColonSightAI — Patient Model
===============================

Defines the Patient database model for clinical record management.

Table: ``patients``

Fields:
    id              : int (PK, auto-increment)
    patient_uid     : str (unique, system-generated, e.g. 'CSAI-20240101-0001')
    first_name      : str (not null)
    last_name       : str (not null)
    date_of_birth   : date
    gender          : str — Male | Female | Other
    contact_number  : str
    email           : str
    address         : text
    medical_history : text
    referring_doctor: str
    notes           : text
    created_by      : int (FK → users.id)
    created_at      : datetime (auto)
    updated_at      : datetime (auto)

Relationships:
    - Many-to-One with User (created_by)
    - One-to-Many with Prediction
"""

# TODO: Implement Patient model
#
# from app.extensions import db
# from datetime import datetime, timezone
#
#
# class Patient(db.Model):
#     \"\"\"Patient clinical record model.\"\"\"
#
#     __tablename__ = 'patients'
#
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     patient_uid = db.Column(db.String(30), unique=True, nullable=False, index=True)
#     first_name = db.Column(db.String(80), nullable=False)
#     last_name = db.Column(db.String(80), nullable=False)
#     date_of_birth = db.Column(db.Date)
#     gender = db.Column(db.String(10))
#     contact_number = db.Column(db.String(20))
#     email = db.Column(db.String(120))
#     address = db.Column(db.Text)
#     medical_history = db.Column(db.Text)
#     referring_doctor = db.Column(db.String(120))
#     notes = db.Column(db.Text)
#     created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
#     created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#     updated_at = db.Column(
#         db.DateTime,
#         default=lambda: datetime.now(timezone.utc),
#         onupdate=lambda: datetime.now(timezone.utc),
#     )
#
#     # ── Relationships ─────────────────────────────────────────────────
#     predictions = db.relationship('Prediction', backref='patient', lazy='dynamic')
#
#     def __repr__(self):
#         return f'<Patient {self.patient_uid}>'
