import sys 
sys.path.insert(1,"src")


import unittest
from src.core.item import Item, Attribute


class Test_Naming_The_Item(unittest.TestCase):

    def test_create_named_item(self):
        item = Item(name="Item 1")
        self.assertEqual(item.name, "Item 1")

    def test_leading_and_trailing_spaces_of_name_are_trimmed(self):
        item = Item(name="  Item A   ")
        self.assertEqual(item.name, "Item A")

    def test_create_item_with_empty_name_raises_error(self):
        self.assertRaises(Item.BlankName, Item, name="")

    def test_renaming_item(self):
        item = Item(name="Item B")
        item.rename(name="Item C")
        self.assertEqual(item.name, "Item C")

    def test_renaming_item_with_blank_name_raises_error(self):
        item = Item(name="Item A")
        self.assertRaises(Item.BlankName, item.rename, "    ")


class Test_Accessing_Item_Attributes(unittest.TestCase):
    
    def test_defining_no_attributes(self)->None:
        item = Item(name="Item A")
        self.assertDictEqual(item.attributes, {})

    def test_defining_attributes(self)->None:
        a1 = Attribute()
        a2 = Attribute()
        item = Item("Item X", attributes={"label_1":a1, "label_2":a2})
        self.assertDictEqual(item.attributes, {"label_1":a1, "label_2":a2})

    def test_default_attribute_type_is_text(self)->None:
        a1 = Attribute()
        self.assertEqual(a1.type,'text')
        
    def test_setting_other_available_type_of_attribute(self)->None:
        a1 = Attribute('integer')
        self.assertEqual(a1.type, 'integer')

    def test_setting_attribute_to_invalid_type_raises_error(self)->None:
        self.assertRaises(Attribute.InvalidType, Attribute, 'invalid_argument_type_0123456789')

    def test_accessing_attribute_value(self)->None:
        a = Attribute('text')
        a.value
    
    def test_setting_the_attribute_value(self)->None:
        a = Attribute('text')
        a.set("Some text.")
        self.assertEqual(a.value, "Some text.")

    def test_valid_value(self)->None:
        a = Attribute('integer')
        self.assertTrue(a.is_valid(5))
        self.assertFalse(a.is_valid("abc"))
        self.assertFalse(a.is_valid("5"))
        self.assertFalse(a.is_valid(""))

    def test_for_text_attribute_any_value_is_valid(self):
        a = Attribute('text')
        self.assertTrue(a.is_valid(5))
        self.assertTrue(a.is_valid("abc"))
        self.assertTrue(a.is_valid("5"))
        self.assertTrue(a.is_valid(""))
        

if __name__=="__main__": unittest.main()