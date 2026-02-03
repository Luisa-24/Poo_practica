# ESTANDAR
from typing import Optional

# TERCEROS
import re


def extract_digits(phone: str) -> str:
    """Extracts only the digits from a phone number.

    Args:
        phone: Phone number to process.

    Returns:
            String containing only digits."""

    try:
        phone_str = str(phone) if phone is not None else ""
        if not phone_str or phone_str.lower() == "nan":
            return ""
        return re.sub(r"\D", "", phone_str)
    except Exception as e:
        print(f"Error extracting digits: {e}")
        return "0000000000"


def phone_is_valid(phone: str) -> bool:
    """Validates whether a phone number has the correct format.
    Accepts phone numbers with 10 digits (US) or 11 digits.

    Args:
        phone: Phone number to validate.

    Returns:
        True if the phone number is valid."""

    try:
        digits = extract_digits(phone)
        if len(digits) == 10:
            return True
        if len(digits) == 11 and digits.startswith("1"):
            return True
        return False
    except Exception as e:
        print(f"Error validating phone: {e}")
        return False


def clean_zeroes(phone: str) -> str:
    """Removes leading zeroes from a phone number.

    Args:
        phone: Phone number to process.
    Returns:
            Phone number without leading zeroes."""

    try:
        digits = extract_digits(phone)
        cleaned = digits.lstrip("0")
        return cleaned
    except Exception as e:
        print(f"Error cleaning zeroes: {e}")
        return phone


def is_negative(phone: str) -> bool:
    """Checks if the phone number is negative.

    Args:
        phone: Phone number to check.
    Returns:
            True if the phone number is negative."""

    try:
        phone_str = str(phone) if phone is not None else ""
        return phone_str.strip().startswith("-")
    except Exception as e:
        print(f"Error checking negative phone: {e}")
        return False


def phone_clean_and_validate(phone: str) -> Optional[str]:
    """Cleans, validates, and formats a phone number.

    Args:
        phone: Phone number to process.

    Returns:
            Formatted phone number if valid, None if invalid."""

    try:
        phone_str = str(phone) if phone is not None else ""
        digits = extract_digits(phone_str)
        cleaned = clean_zeroes(digits)

        if not phone_str or phone_str.lower() == "nan" or not phone_is_valid(cleaned):
            return "0000000000"

        if cleaned:
            return cleaned

        return "0000000000"
    except Exception:
        print(f"Teléfono inválido: {phone}")
        return "0000000000"
