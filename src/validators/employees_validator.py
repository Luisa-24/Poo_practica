# ESTANDAR
from typing import Optional
from datetime import datetime
import sys
import os
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import get_logger
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    PositiveFloat,
    PositiveInt,
)

logger = get_logger(__name__)

# Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

""" this module contains functions to validate Employee objects.

Args:
    A list of Employee objects.
Returns:
    A DataFrame with validation results.
"""


def validate_employees(employees: list) -> "pd.DataFrame":
    """
    Validates a list of Employee objects and returns a DataFrame
    with columns for each relevant validation.

    Args: A list of Employee objects.
    Returns: A DataFrame with validation results."""

    data = []
    for emp in employees:
        row = {
            "employee_id": emp.get("employee_id") or emp.get("_employee_id"),
            "name": emp.get("name") or emp.get("_name"),
            "termination_is_after_hire": termination_is_after_hire(emp),
            "termination_is_after_birthdate": (termination_is_after_birthdate(emp)),
        }
        data.append(row)
    df = pd.DataFrame(data)
    return df


class EmployeeModel(BaseModel):
    """Modelo Pydantic for validated of employee

    Args:
        Full name of the employee.

    Returns:
        An instance of the EmployeeModel class."""

    name: str = Field(..., min_length=1, description="Employee's full name")
    gender: str = Field(..., pattern=r"^(Male|Female|Other)$")
    nationality: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    age: PositiveInt = Field(..., le=120, description="Age must be between 1 and 120")
    birthdate: datetime
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    hire_date: datetime
    contract_type: str = Field(
        ..., pattern=r"^(Full-time|Part-time|Temporary|Freelance)$")
    employee_id: str = Field(..., pattern=r"^EMP\d+$")
    salary: PositiveFloat
    termination_date: datetime


def termination_is_after_hire(employee: dict) -> Optional[bool]:
    """Check if termination date is after hire date  Expects a dict.

    Args:
        Employee data.
    Returns:
            True if termination date is after hire date,
            False otherwise, or None if data is missing or invalid.
    """

    try:
        _hire_date = employee.get("hire_date") or employee.get("_hire_date")
        _termination_date = employee.get("termination_date") or employee.get("_termination_date")
        # Check for missing or NaN values
        if not _hire_date or not _termination_date:
            return None
        if (isinstance(_hire_date, float) and pd.isna(_hire_date)) or (
               isinstance(_termination_date, float) and pd.isna(_termination_date)):
            return None

        # Ensure both are Timestamps
        if not isinstance(_hire_date, pd.Timestamp):
            try:
                _hire_date = pd.to_datetime(_hire_date)
            except Exception:
                return None
        if not isinstance(_termination_date, pd.Timestamp):
            try:
                _termination_date = pd.to_datetime(_termination_date)
            except Exception:
                return None
        days_between = (_termination_date - _hire_date).days
        return days_between >= 1
    except Exception as e:
        raise ValueError(f"Error computing days between hire and termination: {e}")


def termination_is_after_birthdate(employee: dict) -> Optional[bool]:
    """Check if termination date is at least 18
    years after birthdate. Expects a dict.

    Args:
        Employee data.
    Returns:
        True if termination date is at least 18 years after birthdate,
        False otherwise, or None if data is missing or invalid."""

    try:
        _birthdate = employee.get("birthdate") or employee.get("_birthdate")
        _termination_date = employee.get("termination_date") or employee.get("_termination_date")
        # Check for missing or NaN values
        if not _birthdate or not _termination_date:
            return None
        if (isinstance(_birthdate, float) and pd.isna(_birthdate)) or (
                isinstance(_termination_date, float) and pd.isna(_termination_date)):
            return None
        # Ensure both are Timestamps
        if not isinstance(_birthdate, pd.Timestamp):
            try:
                _birthdate = pd.to_datetime(_birthdate)
            except Exception:
                return None
        if not isinstance(_termination_date, pd.Timestamp):
            try:
                _termination_date = pd.to_datetime(_termination_date)
            except Exception:
                return None
        days_between = (_termination_date - _birthdate).days
        years_between = days_between // 365
        return years_between >= 18
    except Exception as e:
        raise ValueError(
            f"Error computing years between termination and birthdate: {e}")
