# ESTANDAR
import sys
import os
import unittest
import pandas as pd

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from cleaners import sales_cleaner


class TestSalesCleaner(unittest.TestCase):
    def test_ensure_datetime(self):
        print("\n--- test_ensure_datetime ---")
        df = pd.DataFrame({"date": ["2020-01-01", "2021-02-02"]})
        print("Input:")
        print(df)
        result = sales_cleaner.ensure_datetime(df, "date")
        print("Output:")
        print(result)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result["date"]))

    def test_clean_data_reassign(self):
        print("\n--- test_clean_data_reassign ---")
        sales_df = pd.DataFrame(
            {
                "sale_id": [1, 2],
                "seller_employee_id": [1, 2],
                "sale_date": ["2022-01-01", "2022-01-02"],
            }
        )
        employees_df = pd.DataFrame(
            {"employee_id": [1, 2], "hire_date": ["2021-01-01", "2022-01-02"]}
        )
        sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
        employees_df["hire_date"] = pd.to_datetime(employees_df["hire_date"])
        print("Sales (input):")
        print(sales_df)
        print("Employees (input):")
        print(employees_df)
        cleaned = sales_cleaner.clean_data(sales_df.copy(), employees_df)
        print("Sales (output):")
        print(cleaned)

        self.assertEqual(cleaned.loc[0, "seller_employee_id"], 1)
        self.assertEqual(cleaned.loc[1, "seller_employee_id"], 2)
