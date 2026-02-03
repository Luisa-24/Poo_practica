# ESTANDAR
import unittest
import os
import sys
import pandas as pd

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from reports.fill_template import generate_employees_pdf


class TestEmployeesReport(unittest.TestCase):
    def test_pdf_generation(self):
        # Create test data
        df_employees = pd.DataFrame(
            {
                "name": ["Alice", "Bob"],
                "email": ["alice@test.com", "bob@test.com"],
                "employee_id": [1, 2],
            }
        )
        df_employees_clean = df_employees.copy()
        validations = pd.DataFrame(
            {"name_valid": [True, True], "email_valid": [True, False]}
        )

        # Generar reporte
        output_dir = "src/reports/output"
        os.makedirs(output_dir, exist_ok=True)

        pdf_path = generate_employees_pdf(
            df_employees,
            df_employees_clean,
            validations,
            employees_created=2,
            output_dir=output_dir,
        )

        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
