# ESTANDAR
import unittest
import os
import sys
import pandas as pd

# Configurar path antes de imports locales
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from reports.fill_template import generate_sales_pdf


class TestSalesReport(unittest.TestCase):
    def test_pdf_generation(self):
        # Crear datos de prueba
        df_sales = pd.DataFrame(
            {
                "sale_id": [1, 2, 3],
                "seller_employee_id": [1, 2, 3],
                "total_price": [100.0, 200.0, 300.0],
            }
        )
        df_sales_clean = df_sales.copy()
        validations = pd.DataFrame(
            {"price_valid": [True, True, False], "seller_valid": [True, False, True]}
        )

        # Generar reporte
        output_dir = "src/reports/output"
        os.makedirs(output_dir, exist_ok=True)

        pdf_path = generate_sales_pdf(
            df_sales, df_sales_clean, validations, sales_created=2, output_dir=output_dir
        )

        self.assertIsNotNone(pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
