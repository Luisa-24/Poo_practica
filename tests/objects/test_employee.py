# ESTANDAR
import unittest
import sys
import os
from datetime import datetime

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from objects.employee import Employee
from validators.employees_validator import validate_employees


class TestEmployee(unittest.TestCase):
    def test_employee_creation_and_validations(self):
        print("\nEmployee creation test:")
        emp = Employee(
            _name="John Doe",
            _gender="Male",
            _nationality="Country",
            _department="Dept",
            _position="Pos",
            _age=30,
            _birthdate=datetime(1990, 1, 1),
            _email="john@example.com",
            _phone="123",
            _address="Addr",
            _hire_date=datetime(2020, 1, 1),
            _contract_type="Full-time",
            _employee_id="EMP1",
            _salary=50000.0,
            _termination_date=datetime(2022, 1, 1),
        )

        print(f"Employee created: {emp.__dict__}")
        self.assertEqual(emp._name, "John Doe")
        self.assertEqual(emp._age, 30)
        self.assertIsInstance(emp._birthdate, datetime)

        print("\nValidating employee with validate_employees...")
        emp_dict = {
            "employee_id": emp._employee_id,
            "name": emp._name,
            "birthdate": emp._birthdate,
            "hire_date": emp._hire_date,
            "termination_date": emp._termination_date,
        }

        df = validate_employees([emp_dict])
        print("Result of validate_employees:")
        print(df)
        self.assertEqual(df.loc[0, "employee_id"], "EMP1")
        self.assertTrue(df.loc[0, "termination_is_after_hire"])
        self.assertTrue(df.loc[0, "termination_is_after_birthdate"])
