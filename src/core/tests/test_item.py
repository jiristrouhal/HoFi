import sys 
sys.path.insert(1,"src")


import unittest
from src.core.item import ItemManager, Item, ItemImpl


NullItem = ItemImpl.NULL


class Test_Naming_The_Item(unittest.TestCase):

    def setUp(self) -> None:
        self.iman = ItemManager()

    def test_create_named_item(self):
        item = self.iman.new(name="Item 1")
        self.assertEqual(item.name, "Item 1")

    def test_leading_and_trailing_spaces_of_name_are_trimmed(self):
        item = self.iman.new(name="  Item A   ")
        self.assertEqual(item.name, "Item A")

    def test_create_item_with_empty_name_raises_error(self):
        self.assertRaises(Item.BlankName, self.iman.new, name="")

    def test_renaming_item(self):
        item = self.iman.new(name="Item B")
        item.rename(name="Item C")
        self.assertEqual(item.name, "Item C")

    def test_grouped_spaces_and_other_in_a_proposed_name_are_automatically_joined_into_single_space(self):
        item = self.iman.new(name="The      Item")
        self.assertEqual(item.name, "The Item")

        item.rename("New        name")
        self.assertEqual(item.name, "New name")

    def test_white_characters_are_replaced_with_spaces(self):
        for c in ('\n','\t','\r','\v','\f'):
            item = self.iman.new(name=f"New{c}name")
            self.assertEqual(item.name, "New name")

    def test_renaming_item_with_blank_name_raises_error(self):
        item = self.iman.new(name="Item A")
        self.assertRaises(Item.BlankName, item.rename, "    ")


class Test_NULL_Item(unittest.TestCase):

    def test_properties(self):
        self.assertDictEqual(NullItem.attribute_values, {})
        self.assertDictEqual(NullItem.attributes, {})
        self.assertEqual(NullItem.name, "")
        self.assertEqual(NullItem.parent, NullItem)

    def test_parent_child_relationships(self):
        self.assertTrue(NullItem.is_predecessor_of(NullItem))
        self.assertTrue(NullItem.is_parent_of(NullItem))

        mg = ItemManager()
        child = mg.new("Child")
        parent = mg.new("Parent")
        self.assertEqual(child.parent, NullItem)
        self.assertEqual(parent.parent, NullItem)
        NullItem.pass_to_new_parent(child,parent)
        self.assertEqual(child.parent, parent)
        
    def test_renaming(self):
        NullItem.rename("New Name")
        self.assertEqual(NullItem.name,"")

    


class Attribute_Mock:
    
    @property
    def value(self)->str: return "Default_Value"


class Test_Accessing_Item_Attributes(unittest.TestCase):

    def setUp(self) -> None:
        self.iman = ItemManager()
        self.a1 = Attribute_Mock()
        self.a2 = Attribute_Mock()
        self.item = self.iman.new("Item X", attributes={"label_1":self.a1, "label_2":self.a2})

    def test_defining_no_attributes(self)->None:
        item = self.iman.new(name="Item X")
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
        mg = ItemManager()
        item = mg.new(name="Apple")
        item.rename("Orange")
        mg.undo()
        self.assertEqual(item.name, "Apple")
        mg.redo()
        self.assertEqual(item.name, "Orange")
        mg.undo()
        self.assertEqual(item.name, "Apple")


class Test_Setting_Parent_Child_Relationship(unittest.TestCase):

    def setUp(self) -> None:
        self.iman = ItemManager()
        self.parent = self.iman.new(name="Parent")
        self.child = self.iman.new(name="Child")
        self.parent.adopt(self.child)

    def test_children_were_added(self):
        not_a_child = self.iman.new(name="Not a Child")
        self.assertTrue(self.parent.is_parent_of(self.child))
        self.assertFalse(self.parent.is_parent_of(not_a_child))
        self.assertEqual(self.child.parent, self.parent)

    def test_repeatedly_adopting_child_does_not_have_effect(self):
        self.parent.adopt(self.child)
        self.assertTrue(self.parent.is_parent_of(self.child))
        self.assertEqual(self.child.parent, self.parent)

    def test_child_having_a_parent_cannot_be_added_to_new_parent(self):
        new_parent = self.iman.new(name="New Parent")
        self.assertEqual(self.child.parent, self.parent)
        new_parent.adopt(self.child)
        self.assertEqual(self.child.parent, self.parent)

    def test_parent_can_pass_child_to_another_parent(self):
        new_parent = self.iman.new(name="New parent")
        self.parent.adopt(self.child)
        self.parent.pass_to_new_parent(self.child,new_parent)
        self.assertEqual(self.child.parent, new_parent)
       
    def test_item_leaving_child_makes_child_forget_the_item_as_its_parent(self):
        self.parent._leave_child(self.child)
        self.assertEqual(self.child.parent, NullItem)

    def test_item_leaving_its_parent_makes_the_parent_forget_is(self):
        self.child._leave_parent(self.parent)
        self.assertEqual(self.child.parent, NullItem)
        self.assertFalse(self.parent.is_parent_of(self.child))

    def test_leaving_parent_not_belonging_to_child_has_no_effect(self)->None:
        not_a_parent = self.iman.new(name="Not a parent")
        self.child._leave_parent(not_a_parent)
        self.assertEqual(self.child.parent, self.parent)

    def test_getting_item_at_the_top_of_family_hierachy(self)->None:
        grandparent = self.iman.new("Grandparent")
        greatgrandparent = self.iman.new("Great-grandparent")

        greatgrandparent.adopt(grandparent)
        grandparent.adopt(self.parent)
        self.parent.adopt(self.child)

        self.assertEqual(self.child.root, greatgrandparent)
        self.assertEqual(grandparent.root, greatgrandparent)
        self.assertEqual(greatgrandparent.root, greatgrandparent)

    def test_after_leaving_parent_the_child_becomes_its_own_root(self):
        self.child._leave_parent(self.parent)
        self.assertEqual(self.child.root, self.child)

    def test_grandparent_and_parent_are_predecesors_of_item(self):
        grandparent = self.iman.new("Grandparent")
        grandparent.adopt(self.parent)
        stranger = self.iman.new("Stranger")
        self.assertTrue(grandparent.is_predecessor_of(self.child))
        self.assertTrue(self.parent.is_predecessor_of(self.child))
        self.assertFalse(self.child.is_predecessor_of(self.parent))
        self.assertFalse(stranger.is_predecessor_of(self.child))
    
    def test_adopting_its_own_predecesor_raises_error(self):
        self.assertRaises(Item.HierarchyCollision, self.child.adopt, self.parent)

        grandchild = self.iman.new("Grandchild")
        self.child.adopt(grandchild)
        self.assertRaises(Item.HierarchyCollision, grandchild.adopt, self.parent)

    def test_leaving_null_has_no_effect(self):
        self.child._leave_parent(self.parent)
        self.assertEqual(self.child.parent, NullItem)
        self.child._leave_parent(NullItem)
        self.assertEqual(self.child.parent, NullItem)

    def test_passing_item_to_its_own_child_raises_error(self):
        grandchild = self.iman.new("Grandchild")
        self.child.adopt(grandchild)
        self.assertRaises(
            Item.HierarchyCollision, 
            self.parent.pass_to_new_parent, 
            self.child,grandchild
        )

class Test_Name_Collisions_Of_Items_With_Common_Parent(unittest.TestCase):

    def setUp(self) -> None:
        self.iman = ItemManager()

    def test_adding_new_child_with_name_already_taken_by_other_child_makes_the_name_to_adjust(self):
        parent = self.iman.new("Parent")
        child = self.iman.new("Child")
        parent.adopt(child)

        child2 = self.iman.new("Child")
        parent.adopt(child2)
        self.assertEqual(child2.name, "Child (1)")

    def test_adding_two_children_with_already_taken_name(self):
        parent = self.iman.new("Parent")
        child = self.iman.new("Child")
        parent.adopt(child)

        child2 = self.iman.new("Child")
        parent.adopt(child2)
        child3 = self.iman.new("Child")
        parent.adopt(child3)

        self.assertEqual(child2.name, "Child (1)")
        self.assertEqual(child3.name, "Child (2)")

    def test_adding_children_differing_in_white_characters(self):
        parent = self.iman.new("Parent")
        child = self.iman.new("The Child")
        parent.adopt(child)

        child2 = self.iman.new("The        Child")
        parent.adopt(child2)
        self.assertEqual(child2.name, "The Child (1)")


class Test_Undo_And_Redo_Setting_Parent_Child_Relationship(unittest.TestCase):

    def setUp(self) -> None:
        self.mg = ItemManager()
        self.parent = self.mg.new("Parent")
        self.child = self.mg.new("Child")
        self.parent.adopt(self.child)

    def test_undo_and_redo_adoption(self):
        self.mg.undo()
        self.assertFalse(self.parent.is_parent_of(self.child))
        self.assertEqual(self.child.parent, NullItem)
        self.mg.redo()
        self.assertTrue(self.parent.is_parent_of(self.child))
        self.assertEqual(self.child.parent, self.parent)
        self.mg.undo()
        self.assertFalse(self.parent.is_parent_of(self.child))
        self.assertEqual(self.child.parent, NullItem)

    def test_undo_and_redo_passing_to_new_parent(self):
        new_parent = self.mg.new("New Parent")
        self.parent.pass_to_new_parent(self.child,new_parent)
        
        self.assertTrue(new_parent.is_parent_of(self.child))
        self.assertFalse(self.parent.has_children())
        self.mg.undo()
        self.assertTrue(self.parent.is_parent_of(self.child))
        self.assertTrue(self.parent.has_children())
        self.assertFalse(new_parent.has_children())
        self.mg.redo()
        self.assertTrue(new_parent.is_parent_of(self.child))
        self.mg.undo()
        self.assertTrue(self.parent.is_parent_of(self.child))

    def test_change_parent_twice_and_then_undo_twice_and_redo_twice(self):
        parent2 = self.mg.new("Parent 2")
        parent3 = self.mg.new("Parent 3")
        self.parent.pass_to_new_parent(self.child, parent2)
        parent2.pass_to_new_parent(self.child, parent3)

        self.assertTrue(parent3.is_parent_of(self.child))

        self.mg.undo()
        self.assertTrue(parent2.is_parent_of(self.child))
        self.assertEqual(self.child.parent, parent2)
        self.mg.undo()
        self.assertTrue(self.parent.is_parent_of(self.child))
        self.assertEqual(self.child.parent, self.parent)

        self.mg.redo()
        self.assertTrue(parent2.is_parent_of(self.child))
        self.assertEqual(self.child.parent, parent2)
        self.mg.redo()
        self.assertTrue(parent3.is_parent_of(self.child))
        self.assertEqual(self.child.parent, parent3)
        #additional redo should not do anything
        self.mg.redo()
        self.assertTrue(parent3.is_parent_of(self.child))

    def test_undo_adoption_when_child_name_was_adjusted(self):
        child2 = self.mg.new("Child")
        self.parent.adopt(child2)
        self.assertEqual(child2.name, "Child (1)")

        self.mg.undo()
        self.assertEqual(child2.name, "Child")
        self.mg.redo()
        self.assertEqual(child2.name, "Child (1)")
        self.mg.undo()
        self.assertEqual(child2.name, "Child")



if __name__=="__main__": unittest.main()







































