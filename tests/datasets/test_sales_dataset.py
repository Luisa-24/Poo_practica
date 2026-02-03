# ESTANDAR
import unittest
import sys
import os
import pandas as pd
import tempfile
from pathlib import Path

# Path - add src directory to path BEFORE imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from datasets.sales_dataset import SalesDataset


class TestSalesDataset(unittest.TestCase):
    def test_init(self):
        ds = SalesDataset("dummy.csv")
        self.assertEqual(ds.source, Path("dummy.csv"))
        self.assertTrue(hasattr(ds, "obj_list"))

    def test_load_data(self):
        # Create a minimal CSV for sales
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as tmp:
            tmp.write(
                "sale_id,product_id,seller_first_name,seller_last_name,"
                "seller_employee_id,buyer_name,sale_date,quantity,unit_price,"
                "total_price,sale_status,employee_id\n"
            )
            tmp.write("1,PROD1,John,Doe,1,Buyer,2022-01-01,2,10.0,20.0,Completed,1\n")
            tmp.flush()
            ds = SalesDataset(tmp.name)
            df = ds.load_data()
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue(len(df) > 0)
        os.unlink(tmp.name)
