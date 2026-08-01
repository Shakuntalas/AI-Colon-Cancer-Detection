"""
ColonSightAI — Utility Function Tests
========================================

Tests for validators, helpers, and other utility modules.
"""

import pytest

from app.utils.validators import (
    is_allowed_file,
    validate_email,
    validate_password_strength,
    sanitize_filename,
)
from app.utils.helpers import (
    generate_uuid,
    generate_short_uid,
    get_file_extension,
    bytes_to_human_readable,
    calculate_percentage,
)


class TestFileValidation:
    """Tests for file validation helpers."""

    @pytest.mark.parametrize('filename,expected', [
        ('image.jpg', True),
        ('image.jpeg', True),
        ('image.png', True),
        ('image.tif', True),
        ('image.tiff', True),
        ('image.bmp', True),
        ('image.gif', False),
        ('image.pdf', False),
        ('image.exe', False),
        ('noextension', False),
        ('', False),
        ('.hidden', False),
    ])
    def test_is_allowed_file(self, filename, expected):
        """Verify file extension validation."""
        assert is_allowed_file(filename) is expected


class TestEmailValidation:
    """Tests for email validation."""

    @pytest.mark.parametrize('email,expected', [
        ('user@example.com', True),
        ('user.name@domain.co.uk', True),
        ('user+tag@example.com', True),
        ('invalid', False),
        ('@domain.com', False),
        ('user@', False),
        ('', False),
    ])
    def test_validate_email(self, email, expected):
        """Verify email format validation."""
        assert validate_email(email) is expected


class TestPasswordValidation:
    """Tests for password strength validation."""

    def test_strong_password_passes(self):
        """A strong password should pass all checks."""
        is_valid, failures = validate_password_strength('Str0ng!Pass')
        assert is_valid is True
        assert len(failures) == 0

    def test_short_password_fails(self):
        """A password shorter than 8 characters should fail."""
        is_valid, failures = validate_password_strength('Ab1!')
        assert is_valid is False
        assert any('8 characters' in f for f in failures)

    def test_no_uppercase_fails(self):
        """A password without uppercase should fail."""
        is_valid, failures = validate_password_strength('abcdefg1!')
        assert is_valid is False


class TestFilenameSanitization:
    """Tests for filename sanitization."""

    def test_removes_path_separators(self):
        """Path separators should be stripped."""
        assert '/' not in sanitize_filename('../../etc/passwd')
        assert '\\' not in sanitize_filename('..\\windows\\system32')

    def test_empty_returns_default(self):
        """Empty filename should return 'unnamed_file'."""
        assert sanitize_filename('') == 'unnamed_file'

    def test_removes_leading_dots(self):
        """Leading dots should be stripped."""
        result = sanitize_filename('.hidden_file.txt')
        assert not result.startswith('.')


class TestHelpers:
    """Tests for helper functions."""

    def test_generate_uuid_is_unique(self):
        """Generated UUIDs should be unique."""
        ids = {generate_uuid() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_short_uid_format(self):
        """Short UID should follow PREFIX-DATE-HASH format."""
        uid = generate_short_uid('TEST')
        parts = uid.split('-')
        assert parts[0] == 'TEST'
        assert len(parts) == 3
        assert len(parts[1]) == 8   # YYYYMMDD
        assert len(parts[2]) == 6   # 6-char hex

    def test_get_file_extension(self):
        """Should extract lowercase extension."""
        assert get_file_extension('image.JPG') == 'jpg'
        assert get_file_extension('noext') == ''

    @pytest.mark.parametrize('size,expected', [
        (0, '0.00 B'),
        (1024, '1.00 KB'),
        (1048576, '1.00 MB'),
        (1073741824, '1.00 GB'),
    ])
    def test_bytes_to_human_readable(self, size, expected):
        """Should convert bytes to readable format."""
        assert bytes_to_human_readable(size) == expected

    def test_calculate_percentage(self):
        """Should calculate percentage correctly."""
        assert calculate_percentage(50, 200) == 25.0
        assert calculate_percentage(0, 0) == 0.0
