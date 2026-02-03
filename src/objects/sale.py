# ESTANDAR
import sys
import os
from datetime import datetime
from dataclasses import dataclass

# Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


@dataclass
class Sale:
    """Represents an individual sale transaction with all relevant data.

    Args:
        Unique identifier for the sale.
    Returns:
        Sale: An instance of the Sale class."""

    _sale_id: str
    _product_id: str
    _seller_first_name: str
    _seller_last_name: str
    _seller_employee_id: str
    _buyer_name: str
    _sale_date: datetime
    _quantity: int
    _unit_price: float
    _total_price: float
    _sale_status: str
