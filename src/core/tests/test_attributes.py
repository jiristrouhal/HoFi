import sys 
sys.path.insert(1,"src")


import unittest
from src.core.attributes import new_attribute, Attribute
from src.cmd.commands import Controller


class Test_Accessing_Item_Attributes(unittest.TestCase):

    def setUp(self) -> None:
        self.controller = Controller()
    
    def test_default_attribute_type_is_text(self)->None:
        a1 = new_attribute(self.controller)
        self.assertEqual(a1.type,'text')
        
    def test_setting_other_available_type_of_attribute(self)->None:
        a1 = new_attribute(self.controller,'integer')
        self.assertEqual(a1.type, 'integer')

    def test_setting_attribute_to_invalid_type_raises_error(self)->None:
        self.assertRaises(Attribute.InvalidAttributeType, new_attribute, self.controller, 'invalid_argument_type_0123456789')

    def test_accessing_attribute_value(self)->None:
        a = new_attribute(self.controller,'text')
        a.value
    
    def test_setting_the_attribute_value(self)->None:
        a = new_attribute(self.controller,'text')
        a.set("Some text.")
        self.assertEqual(a.value, "Some text.")

    def test_valid_value(self)->None:
        a = new_attribute(self.controller,'integer')
        self.assertTrue(a.is_valid(5))
        self.assertFalse(a.is_valid("abc"))
        self.assertFalse(a.is_valid("5"))
        self.assertFalse(a.is_valid(""))

    def test_for_text_attribute_any_value_is_valid(self):
        a = new_attribute(self.controller,'text')
        self.assertTrue(a.is_valid(5))
        self.assertTrue(a.is_valid("abc"))
        self.assertTrue(a.is_valid("5"))
        self.assertTrue(a.is_valid(""))

    def test_setting_attribute_to_an_invalid_value_raises_error(self):
        a = new_attribute(self.controller,'integer')
        self.assertRaises(Attribute.InvalidValueType, a.set, "invalid value")


if __name__=="__main__": unittest.main()