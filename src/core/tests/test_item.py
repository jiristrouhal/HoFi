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
        item.undo()
        self.assertEqual(item.name, "Apple")


class Test_Setting_Parent_Child_Relationship(unittest.TestCase):

    def test_children_were_added(self):
        parent = Item(name="Parent")
        child = Item(name="Child")
        not_a_child = Item(name="Not a Child")
        parent.adopt(child)
        self.assertTrue(parent.is_child(child))
        self.assertFalse(parent.is_child(not_a_child))
        self.assertEqual(child.parent, parent)

    def test_child_having_a_parent_cannot_be_added_to_new_parent(self):
        parent = Item(name="Parent")
        new_parent = Item(name="New Parent")
        child = Item(name="Child")

        parent.adopt(child)
        self.assertEqual(child.parent,parent)
        new_parent.adopt(child)
        self.assertEqual(child.parent,parent)

    def test_parent_can_pass_child_to_another_parent(self):
        parent = Item(name="Parent")
        new_parent = Item(name="New parent")
        child = Item(name="Child")

        parent.adopt(child)
        parent.pass_to_new_parent(child,new_parent)
        self.assertEqual(child.parent, new_parent)
       
    def test_item_leaving_child_makes_child_forget_the_item_as_its_parent(self):
        parent = Item(name="Parent")
        child = Item(name="Child")
        parent.adopt(child)

        parent.leave_child(child)
        self.assertEqual(child.parent,None)

    def test_item_leaving_its_parent_makes_the_parent_forget_is(self):
        parent = Item(name="Parent")
        child = Item(name="Child")
        parent.adopt(child)

        child.leave_parent(parent)
        self.assertEqual(child.parent,None)
        self.assertFalse(parent.is_child(child))



if __name__=="__main__": unittest.main()