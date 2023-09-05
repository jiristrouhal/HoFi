import sys 
sys.path.insert(1,"src")

import core.attributes as attributes
import core.currency as cur
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


class Test_Choice_Attribute(unittest.TestCase):
    
    def setUp(self) -> None:
        self.attrfactory = attributes.Attribute_Factory('en_us')

    def test_storing_the_options_and_the_default_option(self):
        options = {"Go for A":"A", "Go for B":"B"}
        chatt = attributes.Choice_Attribute("Go for A",options)
        self.assertListEqual(chatt.options, list(options.keys()))
        self.assertEqual(chatt.formatted_value, "Go for A")
        self.assertEqual(chatt.value, "A")

    def test_passing_default_option_outside_those_available_raises_key_error(self):
        options = {"Go for A":"A", "Go for B":"B"}
        with self.assertRaises(KeyError):
            attributes.Choice_Attribute("Go for X",options)

    def test_setting_the_option(self):
        options = {"Go for A":"A", "Go for B":"B"}
        chatt = attributes.Choice_Attribute("Go for A",options)
        chatt.set("Go for B")
        self.assertEqual(chatt.formatted_value, "Go for B")
        self.assertEqual(chatt.value, "B")

    def test_automatic_identification_of_this_type_of_attribute(self):
        options = {"Go for A":"A", "Go for B":"B"}
        chatt = self.attrfactory.create_attribute("Go for A", options)
        self.assertEqual(chatt.formatted_value, "Go for A")

class Test_Date_Attribute(unittest.TestCase):
    
    def test_specify_value_on_initialization(self):
        attr = attributes.Date_Attr("01.12.2005",locale_code='cs_cz')
        self.assertEqual(attr.formatted_value, "01.12.2005")

    def test_validate_date(self):
        attr = attributes.Date_Attr(locale_code='cs_cz')
        self.assertTrue(attr.final_validation("1.4.2023"))
        self.assertTrue(attr.final_validation("21.4.2023"))
        self.assertFalse(attr.final_validation(""))
        self.assertFalse(attr.final_validation("   "))

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


class Test_Currency_Attribute(unittest.TestCase):

    def setUp(self) -> None:
        self.attrfac = attributes.Attribute_Factory('en_us')

    def test_defining_attribute(self):
        catt = attributes.Currency_Attribute('USD', 5, 'cs_cz')
        self.assertEqual(catt.value, 5)
        self.assertEqual(catt.formatted_value, '5.00 $')
        catt = attributes.Currency_Attribute('USD', 5, 'en_us')
        self.assertEqual(catt.formatted_value, '$5.00')

    def test_setting_currency(self):
        catt = attributes.Currency_Attribute('USD', 5,'cs_cz')
        self.assertEqual(catt.formatted_value, '5.00 $')
        catt._set_currency('CZK')
        self.assertEqual(catt.formatted_value, '5.00 Kč')

    def test_setting_to_nonexistent_currency_raises_undefined_currency_error(self):
        catt = attributes.Currency_Attribute('USD', 5)
        with self.assertRaises(Exception):
            catt._set_currency('NEC')

    def test_creating_currency_attribute_from_a_general_value(self):
        self.attrfac.set_locale_code('cs_cz')
        catt = self.attrfac.create_attribute("1.00 Kč")
        self.assertEqual(catt.formatted_value,"1.00 Kč")
        catt._set_currency("USD")
        self.assertEqual(catt.formatted_value,"1.00 $")
    
    def test_setting_currency_attribute_value(self):
        self.attrfac.set_locale_code('cs_cz')
        catt = self.attrfac.create_attribute("1 Kč")
        catt.set(5)
        self.assertEqual(catt.formatted_value,"5.00 Kč")

    def test_formatted_value_has_precision_limited_by_the_currency(self):
        self.attrfac.set_locale_code('cs_cz')
        catt = self.attrfac.create_attribute("1 Kč")
        catt.set(0.123456789)
        self.assertEqual(catt.formatted_value,"0.12 Kč")

    def test_attribute_keeps_its_default_currency(self):
        self.attrfac.set_locale_code('cs_cz')
        catt = self.attrfac.create_attribute("1 $")
        self.assertEqual(catt.formatted_value,"1.00 $")

    def test_copying_attribute(self):
        self.attrfac.set_locale_code('cs_cz')
        catt = self.attrfac.create_attribute("2 $")
        self.assertEqual(catt.formatted_value,"2.00 $")
        catt2 = catt.copy()
        self.assertEqual(catt2.formatted_value,"2.00 $")
        catt2.set(45)
        self.assertEqual(catt.formatted_value,"2.00 $")
        self.assertEqual(catt2.formatted_value,"45.00 $")


if __name__=="__main__": unittest.main()