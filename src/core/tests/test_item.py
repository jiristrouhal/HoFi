import sys 
sys.path.insert(1,"src")


import unittest
from src.core.item import Item


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


class Attribute_Mock:
    
    @property
    def value(self)->str: return "Default_Value"


class Test_Accessing_Item_Attributes(unittest.TestCase):

    def setUp(self) -> None:
        self.a1 = Attribute_Mock()
        self.a2 = Attribute_Mock()
        self.item = Item("Item X", attributes={"label_1":self.a1, "label_2":self.a2})

    def test_defining_no_attributes(self)->None:
        item = Item(name="Item X")
        self.assertDictEqual(item.attributes, {})

    def test_defining_attributes(self)->None:
        self.assertDictEqual(self.item.attributes, {"label_1":self.a1, "label_2":self.a2})

    def test_accessing_attribute_values(self)->None:
        self.assertDictEqual(
            self.item.attribute_values, 
            {"label_1": "Default_Value", "label_2": "Default_Value"}
        )

    def test_attributes_cannot_be_removed(self)->None:
        self.item.attributes.clear()
        self.assertDictEqual(
            self.item.attribute_values, 
            {"label_1": "Default_Value", "label_2": "Default_Value"}
        )


class Test_Undo_And_Redo_Renaming(unittest.TestCase):

    def test_single_undo_and_redo(self)->None:
        item = Item(name="Apple")
        item.rename("Orange")
        item.undo()
        self.assertEqual(item.name, "Apple")
        item.redo()
        self.assertEqual(item.name, "Orange")


if __name__=="__main__": unittest.main()