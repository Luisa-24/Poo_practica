# ESTANDAR
import unittest
from datetime import datetime, timedelta
import sys
import os

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from validators.sales_validator import (
    SaleModel,
    is_pending,
    is_completed,
    is_cancelled,
    is_future_date,
    compute_years_to_sale,
    is_older_than_years,
    validate_prices,
    validate_total_price,
)


class DummySale:
    def __init__(
        self,
        sale_status="Pending",
        sale_date=None,
        quantity=1,
        unit_price=10.0,
        total_price=10.0,
    ):
        self.sale_status = sale_status
        self.sale_date = sale_date or datetime.now()
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price


class TestSalesValidator(unittest.TestCase):
    def test_sale_model_valid(self):
        print("\n--- test_sale_model_valid ---")
        data = {
            "sale_id": "SALE123",
            "product_id": "PROD456",
            "seller_first_name": "John",
            "seller_employee_id": "EMP789",
            "sale_date": datetime(2024, 1, 1),
            "quantity": 2,
            "unit_price": 10.0,
            "total_price": 20.0,
            "sale_status": "Completed",
        }
        print(f"Valid input example: {data}")
        model = SaleModel(**data)
        print(f"Result: sale_id={model.sale_id}, sale_status={model.sale_status}")
        self.assertEqual(model.sale_id, "SALE123")
        self.assertEqual(model.sale_status, "Completed")

    def test_is_pending(self):
        print("\n--- test_is_pending ---")
        sale = {"sale_status": "Pending"}
        print(f"Valid input example: {sale}")
        print(f"Result: {is_pending(sale)}")
        self.assertTrue(is_pending(sale))
        sale2 = {"sale_status": "Completed"}
        print(f"Valid input example: {sale2}")
        print(f"Result: {is_pending(sale2)}")
        self.assertFalse(is_pending(sale2))

    def test_is_completed(self):
        print("\n--- test_is_completed ---")
        sale = {"sale_status": "Completed"}
        print(f"Valid input example: {sale}")
        print(f"Result: {is_completed(sale)}")
        self.assertTrue(is_completed(sale))
        sale2 = {"sale_status": "Pending"}
        print(f"Valid input example: {sale2}")
        print(f"Result: {is_completed(sale2)}")
        self.assertFalse(is_completed(sale2))

    def test_is_cancelled(self):
        print("\n--- test_is_cancelled ---")
        sale = {"sale_status": "Cancelled"}
        print(f"Valid input example: {sale}")
        print(f"Result: {is_cancelled(sale)}")
        self.assertTrue(is_cancelled(sale))
        sale2 = {"sale_status": "Completed"}
        print(f"Valid input example: {sale2}")
        print(f"Result: {is_cancelled(sale2)}")
        self.assertFalse(is_cancelled(sale2))

    def test_is_future_date(self):
        print("\n--- test_is_future_date ---")
        future_sale = {"sale_date": datetime.now() + timedelta(days=10)}
        print(f"Valid input example (future): {future_sale}")
        print(f"Result: {is_future_date(future_sale)}")
        self.assertTrue(is_future_date(future_sale))
        past_sale = {"sale_date": datetime.now() - timedelta(days=10)}
        print(f"Valid input example (past): {past_sale}")
        print(f"Result: {is_future_date(past_sale)}")
        self.assertFalse(is_future_date(past_sale))

    def test_compute_years_to_sale(self):
        print("\n--- test_compute_years_to_sale ---")
        hire = datetime(2020, 1, 1)
        sale = datetime(2022, 1, 1)
        print(f"Valid input example: hire={hire}, sale={sale}")
        print(f"Result: {compute_years_to_sale(hire, sale)}")
        self.assertTrue(compute_years_to_sale(hire, sale))
        sale2 = hire + timedelta(days=200)
        print(f"Valid input example: hire={hire}, sale={sale2}")
        print(f"Result: {compute_years_to_sale(hire, sale2)}")
        self.assertFalse(compute_years_to_sale(hire, sale2))

    def test_is_older_than_years(self):
        print("\n--- test_is_older_than_years ---")
        sale = {"sale_date": datetime.now() - timedelta(days=3 * 365)}
        print(f"Valid input example: {sale}, years=2")
        print(f"Result: {is_older_than_years(sale, 2)}")
        self.assertTrue(is_older_than_years(sale, 2))
        print(f"Valid input example: {sale}, years=4")
        print(f"Result: {is_older_than_years(sale, 4)}")
        self.assertFalse(is_older_than_years(sale, 4))

    def test_validate_prices(self):
        print("\n--- test_validate_prices ---")
        sale = {"unit_price": 10.0, "total_price": 20.0}
        print(f"Valid input example: {sale}")
        print(f"Result: {validate_prices(sale)}")
        self.assertTrue(validate_prices(sale))
        sale2 = {"unit_price": -1.0, "total_price": 20.0}
        print(f"Invalid input example: {sale2}")
        print(f"Result: {validate_prices(sale2)}")
        self.assertFalse(validate_prices(sale2))

    def test_validate_total_price(self):
        print("\n--- test_validate_total_price ---")
        sale = {"quantity": 2, "unit_price": 10.0, "total_price": 20.0}
        print(f"Valid input example: {sale}")
        print(f"Result: {validate_total_price(sale)}")
        self.assertTrue(validate_total_price(sale))
        sale2 = {"quantity": 2, "unit_price": 10.0, "total_price": 15.0}
        print(f"Invalid input example: {sale2}")
        print(f"Result: {validate_total_price(sale2)}")
        self.assertFalse(validate_total_price(sale2))
