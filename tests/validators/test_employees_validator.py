# ESTANDAR
import unittest
import sys
import os
from datetime import datetime

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from validators import (
    EmployeeModel,
    termination_is_after_hire,
    termination_is_after_birthdate,)


class DummyEmployee:
    def __init__(self, birthdate, hire_date, termination_date):
        self.birthdate = birthdate
        self.hire_date = hire_date
        self.termination_date = termination_date


class TestEmployeesValidator(unittest.TestCase):
    def test_employee_model_valid(self):
        print("\n--- test_employee_model_valid ---")
        data = {
            "name": "Alice Smith",
            "gender": "Female",
            "age": 30,
            "birthdate": datetime(1995, 1, 1),
            "email": "alice@example.com",
            "hire_date": datetime(2020, 1, 1),
            "contract_type": "Full-time",
            "employee_id": "EMP123",
            "salary": 50000.0,
            "termination_date": datetime(2025, 1, 1),
        }
        print(f"Valid input example: {data}")
        model = EmployeeModel(**data)
        print(
            f"Result: name={model.name}, gender={model.gender}, employee_id={model.employee_id}"
        )
        self.assertEqual(model.name, "Alice Smith")
        self.assertEqual(model.gender, "Female")
        self.assertEqual(model.employee_id, "EMP123")

    def test_termination_is_after_hire(self):
        print("\n--- test_termination_is_after_hire ---")
        emp = {
            "birthdate": datetime(2000, 1, 1),
            "hire_date": datetime(2020, 1, 1),
            "termination_date": datetime(2025, 1, 2),
        }
        print(f"Valid input example: {emp}")
        print(f"Result: {termination_is_after_hire(emp)}")
        self.assertTrue(termination_is_after_hire(emp))
        emp2 = {
            "birthdate": datetime(2000, 1, 1),
            "hire_date": datetime(2020, 1, 1),
            "termination_date": datetime(2020, 1, 1),
        }
        print(f"Invalid input example: {emp2}")
        print(f"Result: {termination_is_after_hire(emp2)}")
        self.assertFalse(termination_is_after_hire(emp2))

    def test_termination_is_after_birthdate(self):
        print("\n--- test_termination_is_after_birthdate ---")
        emp = {
            "birthdate": datetime(2000, 1, 1),
            "hire_date": datetime(2020, 1, 1),
            "termination_date": datetime(2025, 1, 1),
        }
        print(f"Valid input example: {emp}")
        print(f"Result: {termination_is_after_birthdate(emp)}")
        self.assertTrue(termination_is_after_birthdate(emp))
        emp2 = {
            "birthdate": datetime(2010, 1, 1),
            "hire_date": datetime(2020, 1, 1),
            "termination_date": datetime(2025, 1, 1),
        }
        print(f"Invalid input example: {emp2}")
        print(f"Result: {termination_is_after_birthdate(emp2)}")
        self.assertFalse(termination_is_after_birthdate(emp2))
