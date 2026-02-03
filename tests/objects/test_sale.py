# ESTANDAR
import unittest
import sys
import os
from datetime import datetime

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from objects.sale import Sale
from validators.sales_validator import validate_sales


class TestSale(unittest.TestCase):
    def test_sale_creation_and_validations(self):
        sale = Sale(
            _sale_id="SALE1",
            _product_id="PROD1",
            _seller_first_name="John",
            _seller_last_name="Doe",
            _seller_employee_id="EMP1",
            _buyer_name="Buyer",
            _sale_date=datetime(2022, 1, 1),
            _quantity=2,
            _unit_price=10.0,
            _total_price=20.0,
            _sale_status="Completed",
        )
        self.assertEqual(sale._sale_id, "SALE1")
        self.assertEqual(sale._quantity, 2)
        self.assertIsInstance(sale._sale_date, datetime)

        # Convert Sale object to dict for validator
        sale_dict = sale.__dict__
        df = validate_sales([sale_dict])
        self.assertEqual(df.loc[0, "sale_id"], "SALE1")
        self.assertFalse(df.loc[0, "is_pending"])
        self.assertTrue(df.loc[0, "is_completed"])
        self.assertFalse(df.loc[0, "is_cancelled"])
        self.assertFalse(df.loc[0, "is_future_date"])
        self.assertTrue(df.loc[0, "validate_prices"])
        self.assertTrue(df.loc[0, "validate_total_price"])
