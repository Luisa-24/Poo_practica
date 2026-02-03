# ESTANDAR
import sys
import os
import unittest

# Path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)

# LOCALES
from cleaners.field_cleaners import phone_cleaner


class TestFieldPhoneCleaner(unittest.TestCase):
    def test_extract_digits(self):
        self.assertEqual(phone_cleaner.extract_digits("(123) 456-7890"), "1234567890")

    def test_phone_is_valid(self):
        self.assertTrue(phone_cleaner.phone_is_valid("123-456-7890"))
        self.assertFalse(phone_cleaner.phone_is_valid("123"))

    def test_is_negative(self):
        self.assertTrue(phone_cleaner.is_negative("-1234567890"))
        self.assertFalse(phone_cleaner.is_negative("1234567890"))

    def test_phone_clean_and_validate(self):
        # Now returns just digits for valid, '0000000000' for invalid
        self.assertEqual(
            phone_cleaner.phone_clean_and_validate("123-456-7890"), "1234567890"
        )
        # Negative numbers are cleaned to digits, not invalidated
        self.assertEqual(
            phone_cleaner.phone_clean_and_validate("-1234567890"), "1234567890"
        )
