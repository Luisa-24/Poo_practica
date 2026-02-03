# TERCEROS
import gender_guesser.detector as gender  # type: ignore[import-untyped]
import pandas as pd
import sys
from pathlib import Path

# LOCALES
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from cleaners.field_cleaners.email_cleaner import clean
from cleaners.field_cleaners.phone_cleaner import phone_clean_and_validate

logger = get_logger(__name__)

# Global detector
_gender_detector = gender.Detector(case_sensitive=False)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans and validates a DataFrame of employees.

    Args:
        df: DataFrame to clean.

    Returns:
        DataFrame with cleaned data.
    """
    df = df.copy()
    logger.debug(f"Cleaning {len(df)} employee records")
    required_cols = ["employee_id", "name"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.warning(f"Missing columns in DataFrame: {missing_cols}")
    else:
        df.dropna(subset=required_cols, inplace=True)

    if "phone" in df.columns:
        df["phone"] = df["phone"].apply(phone_number_cleaner)
    if "email" in df.columns:
        df["email"] = df["email"].apply(clean_email)
    if "gender" in df.columns and "name" in df.columns:
        df["gender"] = df.apply(
            lambda row: clean_gender_from_name(row["name"], row["gender"]), axis=1
        )
    if "age" in df.columns:
        df = df.drop(columns=["age"])
    return df


def infer_gender_from_name(name: str) -> str:
    """Infers gender from a given name using gender_guesser.

    Args:
        name: Name to infer gender from.
    Returns:
        Inferred gender as 'Male', 'Female', 'Other', or 'Unknown'."""

    try:
        first_name = name.split()[0] if name else ""
        result = _gender_detector.get_gender(first_name)
        if result in ["male", "mostly_male"]:
            return "Male"
        elif result in ["female", "mostly_female"]:
            return "Female"
        elif result == "andy":
            return "Other"
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error inferring gender for '{name}': {e}")
        return "Unknown"


def clean_email(email: str) -> str:
    """Cleans and validates an email address. Only modification:
    set to 'nan' if invalid.

    Args: Email to clean.
    Returns: Cleaned email or 'nan' if invalid."""

    cleaned_email = clean(email)
    return cleaned_email


def phone_number_cleaner(phone: str) -> str:
    """Delegates phone number cleaning to the specialized module.

    Args:
        phone: Phone number to clean.

    Returns:
            Formatted and valid phone number
            or an empty string if invalid."""

    result = phone_clean_and_validate(phone)
    return result if result is not None else ""


def clean_gender_from_name(name, current_gender):
    """Validates and corrects gender based on the name.

    Args:  Employee's name and current gender.
    Returns: Corrected gender if inference differs, else current."""

    inferred = infer_gender_from_name(name)
    if current_gender != inferred:
        return inferred
    return current_gender
