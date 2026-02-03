# Estandar
import sys
import os
import unittest
import pandas as pd

# Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# LOCALES
from cleaners import employees_cleaner


class TestEmployeesCleaner(unittest.TestCase):
    def test_clean_email_valid(self):
        print("\n--- test_clean_email_valid ---")
        email = "  TEST@Example.com "
        result = employees_cleaner.clean_email(email)
        print(f"Input: '{email}' → Output: '{result}'")
        self.assertEqual(result, "test@example.com")

    def test_clean_email_invalid(self):
        print("\n--- test_clean_email_invalid ---")
        email = "invalidemail.com"
        result = employees_cleaner.clean_email(email)
        print(f"Input: '{email}' → Output: '{result}'")
        self.assertEqual(result, "nan")

    def test_clean_email_autocorrect(self):
        print("\n--- test_clean_email_autocorrect ---")
        email = "user.example.com"
        result = employees_cleaner.clean_email(email)
        print(f"Input: '{email}' → Output: '{result}'")
        self.assertEqual(result, "nan")

    def test_phone_number_cleaner_valid(self):
        print("\n--- test_phone_number_cleaner_valid ---")
        phone = "123-456-7890"
        result = employees_cleaner.phone_number_cleaner(phone)
        print(f"Input: '{phone}' → Output: '{result}'")
        self.assertEqual(result, "1234567890")

    def test_phone_number_cleaner_invalid(self):
        print("\n--- test_phone_number_cleaner_invalid ---")
        phone = "abc"
        result = employees_cleaner.phone_number_cleaner(phone)
        print(f"Input: '{phone}' → Output: '{result}'")
        self.assertEqual(result, "0000000000")

    def test_infer_gender_from_name(self):
        print("\n--- test_infer_gender_from_name ---")
        name = "John"
        result = employees_cleaner.infer_gender_from_name(name)
        print(f"Input: '{name}' → Output: '{result}'")
        self.assertIn(result, ["Male", "Unknown", "Other", "Female"])

    def test_clean_gender_from_name(self):
        print("\n--- test_clean_gender_from_name ---")
        name = "Mary"
        current_gender = "Male"
        inferred = employees_cleaner.infer_gender_from_name(name)
        result = employees_cleaner.clean_gender_from_name(name, current_gender)
        print(
            f"Input: name='{name}', current_gender='{current_gender}' → "
            f"Output: '{result}' (expected: '{inferred}')"
        )
        self.assertEqual(result, inferred)

    def test_clean_data_basic(self):
        print("\n--- test_clean_data_basic ---")
        df = pd.DataFrame(
            {
                "employee_id": [1, 2],
                "name": ["John Doe", "Jane Smith"],
                "phone": ["123-456-7890", "555-555-5555"],
                "email": ["JOHN@EXAMPLE.COM", "JANE@EXAMPLE.COM"],
                "gender": ["Male", "Female"],
                "age": [30, 25],
            }
        )
        print("Input:")
        print(df)
        cleaned = employees_cleaner.clean_data(df)
        print("Output:")
        print(cleaned)
        self.assertNotIn("age", cleaned.columns)
        self.assertTrue(all(cleaned["phone"].str.match(r"^[0-9]{10}$|^0000000000$")))
        self.assertTrue(
            all(cleaned["email"].str.islower() | (cleaned["email"] == "nan"))
        )
