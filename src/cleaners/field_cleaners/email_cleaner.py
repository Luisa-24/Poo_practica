# ESTANDAR
from typing import Optional

# TERCEROS
import re


EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def clean(_email: str) -> str:
    """Cleans and normalizes an email. Only modification:
    set to 'nan' if invalid.

    Args:
        Email to clean.
     Returns:
            Cleaned email or 'nan' if invalid."""

    try:
        if not _email:
            return "nan"
        cleaned = _email.strip().lower()
        if not re.match(EMAIL_PATTERN, cleaned):
            return "nan"
        return cleaned
    except Exception:
        return "nan"


def email_is_valid(_email: str) -> bool:
    """Validates whether an email has the correct format.

    Args:
        Email to validate.
    Returns:
            True if email is valid, False otherwise."""

    try:
        if not _email:
            return False
        cleaned = _email.strip().lower()
        return bool(re.match(EMAIL_PATTERN, cleaned))
    except Exception:
        return False


def get_domain(_email: str) -> Optional[str]:
    """Extracts the domain from an email.

    Args:
        email: Email from which to extract the domain.

    Returns:
            Email domain or None if invalid."""

    try:
        if not email_is_valid(_email):
            return None
        return _email.split("@")[1].lower()
    except Exception as e:
        print(f"Error extracting domain: {e}")
        return None
