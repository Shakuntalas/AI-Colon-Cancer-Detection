"""
ColonSightAI — Input Validators
==================================

Validation helper functions for sanitising and verifying user inputs,
uploaded files, and data integrity.
"""

import os
import re
from app.utils.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_FILE_SIZE_BYTES


def is_allowed_file(filename: str) -> bool:
    """
    Check if a filename has an allowed image extension.

    Parameters
    ----------
    filename : str
        The filename to check (e.g., 'image.jpg').

    Returns
    -------
    bool
        True if the extension is in ALLOWED_IMAGE_EXTENSIONS.
    """
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_IMAGE_EXTENSIONS


def validate_file_size(file) -> tuple:
    """
    Validate that an uploaded file is within the size limit.

    Parameters
    ----------
    file : FileStorage
        The uploaded file object.

    Returns
    -------
    tuple[bool, str]
        (is_valid, error_message)
    """
    # Seek to end to determine size, then reset
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE_BYTES:
        return False, (
            f'File size ({file_size / 1024 / 1024:.1f} MB) exceeds '
            f'maximum allowed size ({MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f} MB).'
        )
    if file_size == 0:
        return False, 'Uploaded file is empty.'

    return True, ''


def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Parameters
    ----------
    email : str
        The email address to validate.

    Returns
    -------
    bool
        True if the email format is valid.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple:
    """
    Validate password meets minimum strength requirements.

    Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

    Parameters
    ----------
    password : str
        The password to validate.

    Returns
    -------
    tuple[bool, list[str]]
        (is_valid, list_of_failures)
    """
    failures = []

    if len(password) < 8:
        failures.append('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        failures.append('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        failures.append('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        failures.append('Password must contain at least one digit.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        failures.append('Password must contain at least one special character.')

    return len(failures) == 0, failures


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing unsafe characters.

    Parameters
    ----------
    filename : str
        The original filename.

    Returns
    -------
    str
        Sanitized filename safe for filesystem storage.
    """
    # Remove path separators and null bytes
    filename = filename.replace('/', '').replace('\\', '').replace('\x00', '')
    # Keep only alphanumerics, hyphens, underscores, and dots
    filename = re.sub(r'[^\w\-.]', '_', filename)
    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')
    return filename or 'unnamed_file'
