# ESTANDAR

import pandas as pd
import sys
import os

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from relations.Relations import RelationsValidator


class TestRelationsValidator:
    def setup_method(self):
        # Employees data example
        self.employees_data = {
            "Employee ID": [1, 2, 3],
            "First Name": ["Alice", "Bob", "Charlie"],
            "Last Name": ["Smith", "Johnson", "Williams"],
        }
        self.employees_df = pd.DataFrame(self.employees_data)

        # Sales data example
        self.sales_data = {
            "Sale ID": [101, 102, 103, 104],
            "Seller Employee ID": [1, 2, 4, 3],
            "Seller First Name": ["Alice", "Bob", "David", "Charlie"],
            "Seller Last Name": ["Smith", "Johnson", "Brown", "Williams"],
        }

        self.sales_df = pd.DataFrame(self.sales_data)

        self.validator = RelationsValidator(self.employees_df, self.sales_df)

    def test_validate_employee_without_sales(self):
        result = self.validator.validate_employee_without_sales()
        assert len(result) == 0
        print("Employees without sales:", result)

    def test_validate_employee_ids_in_sales(self):
        result = self.validator.validate_employee_ids_in_sales()
        assert len(result) == 1
        assert result.iloc[0]["Seller Employee ID"] == 4
        print("Sales with invalid IDs:", result)

    def test_validate_employee_names_in_sales(self):
        result = self.validator.validate_employee_names_in_sales()
        assert len(result) == 1  # There is a sale with invalid name/last name
        assert result.iloc[0]["Seller Employee ID"] == 4
        print("Sales with invalid names/last names:", result)

    def test_validate_count_employees_without_sales(self):
        result = self.validator.validate_count_employees_without_sales()
        assert isinstance(result, int)
        print("Number of employees without sales:", result)
