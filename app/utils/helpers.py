"""
ColonSightAI — Helper Functions
==================================

Miscellaneous utility functions used across the application.
"""

import os
import uuid
from datetime import datetime, timezone

from app.utils.constants import DATETIME_FORMAT, DISPLAY_DATETIME_FORMAT


def generate_uuid() -> str:
    """Generate a unique identifier string."""
    return str(uuid.uuid4())


def generate_short_uid(prefix: str = 'CSAI') -> str:
    """
    Generate a short unique identifier with a prefix.

    Format: ``{prefix}-{YYYYMMDD}-{short_uuid}``

    Example: ``CSAI-20240815-a1b2c3``
    """
    date_part = datetime.now(timezone.utc).strftime('%Y%m%d')
    short_id = uuid.uuid4().hex[:6]
    return f'{prefix}-{date_part}-{short_id}'


def get_timestamp() -> str:
    """Return the current UTC timestamp as a formatted string."""
    return datetime.now(timezone.utc).strftime(DATETIME_FORMAT)


def format_datetime(dt: datetime, display: bool = False) -> str:
    """
    Format a datetime object as a string.

    Parameters
    ----------
    dt : datetime
        The datetime to format.
    display : bool
        If True, use display-friendly format. Otherwise, ISO-style.

    Returns
    -------
    str
        The formatted datetime string.
    """
    fmt = DISPLAY_DATETIME_FORMAT if display else DATETIME_FORMAT
    return dt.strftime(fmt)


def get_file_extension(filename: str) -> str:
    """Extract the lowercase file extension from a filename."""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def ensure_directory(path: str) -> None:
    """Create a directory and its parents if they don't exist."""
    os.makedirs(path, exist_ok=True)


def bytes_to_human_readable(size_bytes: int) -> str:
    """
    Convert bytes to a human-readable string.

    Examples: ``1024 → '1.00 KB'``, ``1048576 → '1.00 MB'``
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f'{size_bytes:.2f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.2f} TB'


def calculate_percentage(part: float, whole: float, decimals: int = 2) -> float:
    """Calculate percentage safely, returning 0.0 if whole is zero."""
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, decimals)
