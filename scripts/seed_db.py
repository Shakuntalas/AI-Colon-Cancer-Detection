"""
ColonSightAI — Database Seeding Script
=========================================

Populates the database with initial/sample data for development.

Usage:
    python scripts/seed_db.py

This script:
    1. Creates the admin user account
    2. Adds sample patient records
    3. Inserts demo prediction results (optional)

WARNING: Running this script will insert new records. Existing data
will NOT be deleted unless --reset flag is passed.
"""

# TODO: Implement database seeding
#
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#
# from app import create_app
# from app.extensions import db
# from app.models.user import User
# from app.models.patient import Patient
#
#
# def seed_admin():
#     """Create the default admin account."""
#     admin = User(
#         username='admin',
#         email='admin@colonsightai.com',
#         password_hash='<hashed>',
#         first_name='System',
#         last_name='Administrator',
#         role='admin',
#     )
#     db.session.add(admin)
#     db.session.commit()
#     print('[+] Admin user created.')
#
#
# def seed_sample_patients():
#     """Insert sample patient records for development."""
#     # TODO: Add 5-10 sample patients
#     pass
#
#
# if __name__ == '__main__':
#     app = create_app('development')
#     with app.app_context():
#         db.create_all()
#         seed_admin()
#         seed_sample_patients()
#         print('[✓] Database seeding complete.')

print('Database seeding script — not yet implemented.')
print('Uncomment the code above after implementing database models.')
