import sys
sys.path.insert(1,"src")

import unittest
import src.core.currency as cur


class Test_Recognizing_Currency(unittest.TestCase):

    def test_valid_currencies(self):
        self.assertTrue(cur.convert_to_currency("10 Kč"))
        self.assertTrue(cur.convert_to_currency("10 $"))
        self.assertTrue(cur.convert_to_currency("10. $"))
        self.assertTrue(cur.convert_to_currency("10, $"))
        self.assertTrue(cur.convert_to_currency("10.0 $"))
        self.assertTrue(cur.convert_to_currency("10.1234564984654651 $"))
        self.assertTrue(cur.convert_to_currency("10.0       $"))
        self.assertTrue(cur.convert_to_currency("10.0$"))
        self.assertTrue(cur.convert_to_currency("10,0$"))

        self.assertTrue(cur.convert_to_currency("$ 10"))
        self.assertTrue(cur.convert_to_currency("$ 10.0000"))
        self.assertTrue(cur.convert_to_currency("$10.0000"))

    
    def test_missing_leading_digit_is_ok(self):
        self.assertTrue(cur.convert_to_currency("$.0000"))
        self.assertTrue(cur.convert_to_currency(".0000$"))

    def test_double_separator_is_invalid(self):
        self.assertFalse(cur.convert_to_currency("10.."))

    def test_missing_currency_symbol(self):
        self.assertFalse(cur.convert_to_currency("10"))
        self.assertFalse(cur.convert_to_currency("20"))
        self.assertFalse(cur.convert_to_currency("10.00"))
        self.assertFalse(cur.convert_to_currency("  10.00"))
        self.assertFalse(cur.convert_to_currency("10.00   "))

    def test_no_number(self):
        self.assertFalse(cur.convert_to_currency(""))
        self.assertFalse(cur.convert_to_currency("asdf"))

    def test_invalid_currency_symbols(self):
        self.assertFalse(cur.convert_to_currency("abc 20"))
        self.assertFalse(cur.convert_to_currency("10abc"))
        self.assertFalse(cur.convert_to_currency("123_"))
        self.assertFalse(cur.convert_to_currency("50.23 crowns"))
    
    def test_garbage_text_near_the_currency(self):
        self.assertFalse(cur.convert_to_currency("Lorem ipsum 20 $"))
        self.assertFalse(cur.convert_to_currency("20 $ sit amet"))


if __name__=="__main__": unittest.main()