import sys 
sys.path.insert(1,"src")

import attributes
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


import dates
class Test_Date_Attribute(unittest.TestCase):
    
    def setUp(self) -> None:
        attributes.Date_Attr.date_formatter.set("%d.%m.%Y")
        self.attr = attributes.Date_Attr()

    def test_specify_value_on_initialization(self):
        attr = attributes.Date_Attr("01.12.2005")
        self.assertEqual(attr.value, "01.12.2005")

    def test_validate_date(self):
        attr = attributes.Date_Attr()
        self.assertTrue(attr.valid_entry("1.4.2023"))
        self.assertTrue(attr.valid_entry("21.4.2023"))
        self.assertTrue(attr.valid_entry(""))
        self.assertTrue(attr.valid_entry("   "))

        self.assertFalse(attr.valid_entry("31.4.2023"))
        self.assertFalse(attr.valid_entry(".4.2023"))



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