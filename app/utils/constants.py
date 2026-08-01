"""
ColonSightAI — Application Constants
=======================================

Centralised constants, enumerations, and status codes used throughout
the application. Avoids magic strings and numbers in business logic.
"""

from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════
# Application Metadata
# ═══════════════════════════════════════════════════════════════════════════
APP_NAME = 'ColonSightAI'
APP_VERSION = '1.0.0'
APP_DESCRIPTION = (
    'Explainable Clinical Decision Support System for '
    'Colon Cancer Detection Using Deep Learning'
)
APP_AUTHOR = 'ColonSightAI Research Team'

# ═══════════════════════════════════════════════════════════════════════════
# User Roles
# ═══════════════════════════════════════════════════════════════════════════


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = 'admin'
    CLINICIAN = 'clinician'
    RESEARCHER = 'researcher'


# ═══════════════════════════════════════════════════════════════════════════
# Prediction Status
# ═══════════════════════════════════════════════════════════════════════════


class PredictionStatus(str, Enum):
    """Prediction processing status."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


# ═══════════════════════════════════════════════════════════════════════════
# File Upload
# ═══════════════════════════════════════════════════════════════════════════
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff', 'bmp'}
MAX_FILE_SIZE_MB = 16
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ═══════════════════════════════════════════════════════════════════════════
# Pagination
# ═══════════════════════════════════════════════════════════════════════════
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ═══════════════════════════════════════════════════════════════════════════
# Flash Message Categories
# ═══════════════════════════════════════════════════════════════════════════
FLASH_SUCCESS = 'success'
FLASH_ERROR = 'error'
FLASH_WARNING = 'warning'
FLASH_INFO = 'info'

# ═══════════════════════════════════════════════════════════════════════════
# HTTP Status Codes (semantic aliases)
# ═══════════════════════════════════════════════════════════════════════════
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE = 422
HTTP_TOO_LARGE = 413
HTTP_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501

# ═══════════════════════════════════════════════════════════════════════════
# Date / Time Formats
# ═══════════════════════════════════════════════════════════════════════════
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
DISPLAY_DATETIME_FORMAT = '%d %b %Y, %I:%M %p'
