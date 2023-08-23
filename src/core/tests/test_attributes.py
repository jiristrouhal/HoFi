import sys 
sys.path.insert(1,"src")

import core.attributes as attributes
import unittest


class Test_Positive_Int_Attribute(unittest.TestCase):

    def setUp(self) -> None:
        self.attr = attributes.Positive_Int_Attr()
        self.assertEqual(self.attr.value, int(attributes.Positive_Int_Attr.default_value))

    def test_value_validation(self):
        self.assertTrue(self.attr.valid_entry("1"))
        self.assertFalse(self.attr.valid_entry("  1"))
        self.assertTrue(self.attr.valid_entry("5"))
        self.assertFalse(self.attr.valid_entry("5.0"))
        self.assertFalse(self.attr.valid_entry("0"))
        self.assertFalse(self.attr.valid_entry("0.5"))
        self.assertFalse(self.attr.valid_entry("-1"))
        self.assertFalse(self.attr.valid_entry("-8"))
        self.assertTrue(self.attr.valid_entry( 5))

    def test_value_setting(self):
        self.attr.set("50")
        self.assertEqual(self.attr.value, 50)
        self.attr.set("10")
        self.assertEqual(self.attr.value,10)
        self.attr.set()
        self.assertEqual(self.attr.value,10)

class Test_Recognizing_Currency(unittest.TestCase):

    def test_valid_currencies_with(self):
        self.assertTrue(attributes.is_currency("10 Kč"))
        self.assertTrue(attributes.is_currency("10 $"))
        self.assertTrue(attributes.is_currency("10. $"))
        self.assertTrue(attributes.is_currency("10, $"))
        self.assertTrue(attributes.is_currency("10.0 $"))
        self.assertTrue(attributes.is_currency("10.1234564984654651 $"))
        self.assertTrue(attributes.is_currency("10.0       $"))
        self.assertTrue(attributes.is_currency("10.0$"))
        self.assertTrue(attributes.is_currency("10,0$"))

        self.assertTrue(attributes.is_currency("$ 10"))
        self.assertTrue(attributes.is_currency("$ 10.0000"))
        self.assertTrue(attributes.is_currency("$10.0000"))

    
    def test_missing_leading_digit_is_ok(self):
        self.assertTrue(attributes.is_currency("$.0000"))
        self.assertTrue(attributes.is_currency(".0000$"))

    def test_double_separator_is_invalid(self):
        self.assertFalse(attributes.is_currency("10.."))

    def test_missing_currency_symbol(self):
        self.assertFalse(attributes.is_currency("10"))
        self.assertFalse(attributes.is_currency("20"))
        self.assertFalse(attributes.is_currency("10.00"))
        self.assertFalse(attributes.is_currency("  10.00"))
        self.assertFalse(attributes.is_currency("10.00   "))

    def test_no_number(self):
        self.assertFalse(attributes.is_currency(""))
        self.assertFalse(attributes.is_currency("asdf"))

    def test_invalid_currency_symbols(self):
        self.assertFalse(attributes.is_currency("abc 20"))
        self.assertFalse(attributes.is_currency("10abc"))
        self.assertFalse(attributes.is_currency("123_"))
        self.assertFalse(attributes.is_currency("50.23 crowns"))
    
    def test_garbage_text_near_the_currency(self):
        self.assertFalse(attributes.is_currency("Lorem ipsum 20 $"))
        self.assertFalse(attributes.is_currency("20 $ sit amet"))
        


class Test_Date_Attribute(unittest.TestCase):
    
    def setUp(self) -> None:
        attributes.Date_Attr.date_formatter.set("%d.%m.%Y")
        self.attr = attributes.Date_Attr()

    def test_specify_value_on_initialization(self):
        attr = attributes.Date_Attr("01.12.2005")
        self.assertEqual(attr.value, "01.12.2005")

    def test_validate_date(self):
        attr = attributes.Date_Attr()
        self.assertTrue(attr.final_validation("1.4.2023"))
        self.assertTrue(attr.final_validation("21.4.2023"))
        self.assertTrue(attr.final_validation(""))
        self.assertTrue(attr.final_validation("   "))

        self.assertFalse(attr.final_validation("31.4.2023"))
        self.assertFalse(attr.final_validation(".4.2023"))



class Test_Name_Attribute(unittest.TestCase):

    def setUp(self) -> None:
        self.attr = attributes.Name_Attr()
        self.assertEqual(self.attr.value, attributes.Name_Attr.default_value)

    def test_specify_value_on_initialization(self):
        attr = attributes.Name_Attr("SomeName")
        self.assertEqual(attr.value, "SomeName")

    def test_value_validation(self):
        self.assertTrue(self.attr.valid_entry("Something"))
        self.assertTrue(self.attr.valid_entry("Some  Thing"))
        self.assertTrue(self.attr.valid_entry("Something     "))
        self.assertFalse(self.attr.valid_entry("   Something"))

        self.assertFalse(self.attr.valid_entry("1223456"))
        self.assertTrue(self.attr.valid_entry("ABC1223456"))

        self.assertFalse(self.attr.valid_entry(" "))
        self.assertTrue(self.attr.valid_entry("_"))

        self.assertFalse(self.attr.valid_entry("5a"))
        self.assertTrue(self.attr.valid_entry("a5"))
        self.assertTrue(self.attr.valid_entry("_5a"))

        self.assertFalse(self.attr.valid_entry("+"))
        self.assertFalse(self.attr.valid_entry("-"))

    def test_value_setting(self):
        self.attr.set("A")
        self.assertEqual(self.attr.value,"A")
        self.attr.set("6")
        self.assertEqual(self.attr.value,"A")


if __name__=="__main__": unittest.main()