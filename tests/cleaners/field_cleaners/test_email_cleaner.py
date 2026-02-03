# ESTANDAR
import sys
import os
import unittest

# Path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)

# LOCALES
from cleaners.field_cleaners import email_cleaner


class TestFieldEmailCleaner(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(email_cleaner.clean("  TEST@Example.com "), "test@example.com")

    def test_email_is_valid(self):
        self.assertTrue(email_cleaner.email_is_valid("test@example.com"))
        self.assertFalse(email_cleaner.email_is_valid("invalidemail"))

    def test_get_domain(self):
        self.assertEqual(email_cleaner.get_domain("user@domain.com"), "domain.com")
        self.assertIsNone(email_cleaner.get_domain("invalidemail"))
