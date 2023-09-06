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

    def test_grouped_spaces_and_other_in_a_proposed_name_are_automatically_joined_into_single_space(self):
        item = Item(name="The      Item")
        self.assertEqual(item.name, "The Item")

        item.rename("New        name")
        self.assertEqual(item.name, "New name")

    def test_white_characters_are_replaced_with_spaces(self):
        for c in ('\n','\t','\r','\v','\f'):
            item = Item(name=f"New{c}name")
            self.assertEqual(item.name, "New name")

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

    def setUp(self) -> None:
        self.parent = Item(name="Parent")
        self.child = Item(name="Child")
        self.parent.adopt(self.child)

    def test_children_were_added(self):
        not_a_child = Item(name="Not a Child")
        self.assertTrue(self.parent.is_child(self.child))
        self.assertFalse(self.parent.is_child(not_a_child))
        self.assertEqual(self.child.parent, self.parent)

    def test_repeatedly_adopting_child_does_not_have_effect(self):
        self.parent.adopt(self.child)
        self.assertTrue(self.parent.is_child(self.child))
        self.assertEqual(self.child.parent, self.parent)

    def test_child_having_a_parent_cannot_be_added_to_new_parent(self):
        new_parent = Item(name="New Parent")
        self.assertEqual(self.child.parent, self.parent)
        new_parent.adopt(self.child)
        self.assertEqual(self.child.parent, self.parent)

    def test_parent_can_pass_child_to_another_parent(self):
        new_parent = Item(name="New parent")
        self.parent.adopt(self.child)
        self.parent.pass_to_new_parent(self.child,new_parent)
        self.assertEqual(self.child.parent, new_parent)
       
    def test_item_leaving_child_makes_child_forget_the_item_as_its_parent(self):
        self.parent.leave_child(self.child)
        self.assertEqual(self.child.parent,None)

    def test_item_leaving_its_parent_makes_the_parent_forget_is(self):
        self.child.leave_parent(self.parent)
        self.assertEqual(self.child.parent,None)
        self.assertFalse(self.parent.is_child(self.child))

    def test_leaving_parent_not_belonging_to_child_has_no_effect(self)->None:
        not_a_parent = Item(name="Not a parent")
        self.child.leave_parent(not_a_parent)
        self.assertEqual(self.child.parent, self.parent)

    def test_getting_item_at_the_top_of_family_hierachy(self)->None:
        grandparent = Item("Grandparent")
        greatgrandparent = Item("Great-grandparent")

        greatgrandparent.adopt(grandparent)
        grandparent.adopt(self.parent)
        self.parent.adopt(self.child)

        self.assertEqual(self.child.root, greatgrandparent)
        self.assertEqual(grandparent.root, greatgrandparent)
        self.assertEqual(greatgrandparent.root, greatgrandparent)

    def test_after_leaving_parent_the_child_becomes_its_own_root(self):
        self.child.leave_parent(self.parent)
        self.assertEqual(self.child.root, self.child)

    def test_grandparent_and_parent_are_predecesors_of_item(self):
        grandparent = Item("Grandparent")
        grandparent.adopt(self.parent)
        stranger = Item("Stranger")
        self.assertTrue(grandparent.is_predecessor_of(self.child))
        self.assertTrue(self.parent.is_predecessor_of(self.child))
        self.assertFalse(self.child.is_predecessor_of(self.parent))
        self.assertFalse(stranger.is_predecessor_of(self.child))
    
    def test_adopting_its_own_predecesor_raises_error(self):
        self.assertRaises(Item.HierarchyCollision, self.child.adopt, self.parent)

        grandchild = Item("Grandchild")
        self.child.adopt(grandchild)
        self.assertRaises(Item.HierarchyCollision, grandchild.adopt, self.parent)


class Test_Name_Collisions_Of_Items_With_Common_Parent(unittest.TestCase):

    def test_adding_new_child_with_name_already_taken_by_other_child_makes_the_name_to_adjust(self):
        parent = Item("Parent")
        child = Item("Child")
        parent.adopt(child)

        child2 = Item("Child")
        parent.adopt(child2)
        self.assertEqual(child2.name, "Child (1)")

    def test_adding_two_children_with_already_taken_name(self):
        parent = Item("Parent")
        child = Item("Child")
        parent.adopt(child)

        child2 = Item("Child")
        parent.adopt(child2)
        child3 = Item("Child")
        parent.adopt(child3)

        self.assertEqual(child2.name, "Child (1)")
        self.assertEqual(child3.name, "Child (2)")

    def test_adding_children_differing_in_white_characters(self):
        parent = Item("Parent")
        child = Item("The Child")
        parent.adopt(child)

        child2 = Item("The        Child")
        parent.adopt(child2)
        self.assertEqual(child2.name, "The Child (1)")
    


if __name__=="__main__": unittest.main()