# ESTANDAR
from datetime import datetime
from typing import Optional
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import get_logger

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    PositiveInt,
)

logger = get_logger(__name__)

"""
Sale Pydantic Model - for validation of sale data.

This module contains functions to validate Sale objects.
"""


def validate_sales(sales: list) -> "pd.DataFrame":
    """
    Validates a list of Sale objects and returns a DataFrame
    with columns for each relevant validation.
    Columns:
        - is_pending: bool
        - is_completed: bool
        - is_cancelled: bool
        - is_future_date: bool
        - validate_prices: bool
        - validate_total_price: bool
    """
    data = []
    for sale in sales:
        row = {
            "sale_id": sale.get("sale_id") or sale.get("_sale_id"),
            "product_id": sale.get("product_id") or sale.get("_product_id"),
            "is_pending": is_pending(sale),
            "is_completed": is_completed(sale),
            "is_cancelled": is_cancelled(sale),
            "is_future_date": is_future_date(sale),
            "validate_prices": validate_prices(sale),
            "validate_total_price": validate_total_price(sale),
        }
        data.append(row)
    df = pd.DataFrame(data)
    return df


class SaleModel(BaseModel):
    """Pydantic model for validation of sale data.

    Args:
        Unique identifier for the sale.

    Returns:
           An instance of the SaleModel class."""

    sale_id: str = Field(..., pattern=r"^SALE\d+$")
    product_id: str = Field(..., pattern=r"^PROD\d+$")
    seller_first_name: str = Field(..., min_length=1)
    seller_last_name: Optional[str] = None
    seller_employee_id: str = Field(..., pattern=r"^EMP\d+$")
    buyer_name: Optional[str] = None
    sale_date: datetime
    quantity: PositiveInt
    unit_price: PositiveFloat
    total_price: PositiveFloat
    sale_status: str = Field(..., pattern=r"^(Completed|Pending|Cancelled)$")


def is_pending(sale) -> bool:
    """Check if the sale status is 'Pending'.

    Args:
        sale: The Sale instance to check.

    Returns:
        bool: True if sale is pending.
    """
    try:
        status = sale.get("sale_status") or sale.get("_sale_status")
        if isinstance(status, str):
            return status.strip().lower() == "pending"
        return False
    except Exception as e:
        print(f"Error checking pending status: {e}")
        return False


def is_completed(sale) -> bool:
    """Check if the sale status is 'Completed'.

    Args:
        sale: The Sale instance to check.

    Returns:
        bool: True if sale is completed.
    """
    try:
        status = sale.get("sale_status") or sale.get("_sale_status")
        if isinstance(status, str):
            return status.strip().lower() == "completed"
        return False
    except Exception as e:
        print(f"Error checking completed status: {e}")
        return False


def is_cancelled(sale) -> bool:
    """Check if the sale status is 'Cancelled'.

    Args:
        sale: The Sale instance to check.

    Returns:
        bool: True if sale is cancelled.
    """
    try:
        status = sale.get("sale_status") or sale.get("_sale_status")
        valid_statuses = ["cancelled", "canceled"]
        return status.lower() in valid_statuses if status else False
    except Exception as e:
        print(f"Error checking cancelled status: {e}")
        return False


def is_future_date(sale, reference_date: Optional[datetime] = None) -> bool:
    """Check if the sale date is in the future.

    Args:
        sale: The Sale instance to check.
        reference_date: Date to compare against (defaults to today).

    Returns:
        bool: True if sale date is in the future.
    """

    try:
        _sale_date = sale.get("sale_date") or sale.get("_sale_date")
        if not _sale_date:
            return False
        ref_date = reference_date or datetime.now()
        return _sale_date > ref_date
    except Exception as e:
        print(f"Error checking future date: {e}")
        return False


def compute_years_to_sale(_hire_date: datetime, _sale_date: datetime) -> Optional[bool]:
    """Calculate years between hire date and sale date.

    Args:
        hire_date: Employee's hire date.
        sale_date: Sale date.
    Returns:
        bool: True if years between hire and sale is at least 1, False if less.
    """
    try:
        if not _hire_date or not _sale_date:
            return None

        days_between = (_sale_date - _hire_date).days
        years_between = days_between // 365
        return years_between >= 1
    except Exception as e:
        raise ValueError(f"Error computing years between hire and sale: {e}")


def is_older_than_years(sale,years: int,reference_date: Optional[datetime] = None) -> bool:

    """Check if the sale is older than a specified number of years.

    Args:
        sale: The Sale instance to check.
        years: Number of years to check against.
        reference_date: Date to compare against (defaults to today).
    Returns:
        bool: True if sale is older than specified years.
    """
    try:
        _sale_date = sale.get("sale_date") or sale.get("_sale_date")
        if not _sale_date:
            return False
        ref_date = reference_date or datetime.now()
        years_diff = (ref_date - _sale_date).days // 365
        return years_diff > years
    except Exception as e:
        print(f"Error checking if sale is older than years: {e}")
        return False


def validate_prices(sale) -> bool:
    """Validate that prices are non-negative.

    Args:
        sale: The Sale instance to validate.

    Returns:
        bool: True if unit_price and total_price are non-negative.
    """
    try:
        _unit_price = sale.get("unit_price") or sale.get("_unit_price")
        _total_price = sale.get("total_price") or sale.get("_total_price")
        return (
            _unit_price >= 0 and _total_price >= 0
            if _unit_price is not None and _total_price is not None
            else False)
    except Exception as e:
        print(f"Error validating prices: {e}")
        return False


def validate_total_price(sale) -> bool:
    """Validate that total_price equals quantity * unit_price.

    Args:
        sale: The Sale instance to validate.

    Returns:
        bool: True if total_price is correctly calculated.
    """
    try:
        _quantity = sale.get("quantity") or sale.get("_quantity")
        _unit_price = sale.get("unit_price") or sale.get("_unit_price")
        _total_price = sale.get("total_price") or sale.get("_total_price")
        if _quantity is None or _unit_price is None or _total_price is None:
            return False
        expected_total = _quantity * _unit_price
        return abs(_total_price - expected_total) < 0.01
    except Exception as e:
        print(f"Error validating total price: {e}")
        return False
