# ESTANDAR
import unittest
import sys
import os
import pandas as pd
import tempfile
from pathlib import Path

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from datasets.employees_dataset import EmployeesDataset


class TestEmployeesDataset(unittest.TestCase):
    def test_init(self):
        ds = EmployeesDataset("dummy.csv")
        self.assertEqual(ds.source, Path("dummy.csv"))
        self.assertTrue(hasattr(ds, "obj_list"))

    def test_load_data(self):
        # Create a minimal CSV for employees
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as tmp:
            tmp.write(
                "Employee ID,Name,Gender,Nationality,Department,Position,Age,"
                "Birthdate,Email,Phone,Address,Hire Date,Contract Type,Salary,"
                "Termination Date\n"
            )
            tmp.write(
                "1,John Doe,Male,Country,Dept,Pos,30,1990-01-01,"
                "john@example.com,123,Addr,2020-01-01,Full,50000,"
                "2022-01-01\n"
            )
            tmp.flush()
            ds = EmployeesDataset(tmp.name)
            df = ds.load_data()
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue(len(df) > 0)
        os.unlink(tmp.name)
