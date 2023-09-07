from __future__ import annotations


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
        self.assertEqual(NullItem.root, NullItem)

    def test_parent_child_relationships(self):
        self.assertTrue(NullItem.is_predecessor_of(NullItem))
        self.assertTrue(NullItem.is_parent_of(NullItem))

        self.assertTrue(NullItem.has_children())

        mg = ItemManager()
        child = mg.new("Child")
        parent = mg.new("Parent")
        self.assertEqual(child.parent, NullItem)
        self.assertEqual(parent.parent, NullItem)
        NullItem.pass_to_new_parent(child,parent)
        self.assertEqual(child.parent, parent)

        self.assertEqual(NullItem.get_copy(), NullItem)

    def test_leaving_child_has_no_effect(self):
        mg = ItemManager()
        child = mg.new("Child")
        self.assertTrue(NullItem.is_parent_of, child)
        NullItem._leave_child(child)
        self.assertTrue(NullItem.is_parent_of, child)

    def test_leaving_parent_has_no_effect(self):
        mg = ItemManager()
        NullItem._leave_parent(NullItem)
        self.assertTrue(NullItem.is_parent_of, NullItem)

    def test_adding_null_item_under_a_nonnull_parent_raises_error(self):
        mg = ItemManager()
        parent = mg.new("Parent")
        self.assertRaises(Item.AdoptingNULL, parent.adopt, NullItem)
        self.assertRaises(Item.AdoptingNULL, NullItem._adopt_by, parent)
        
    def test_adopting_child_by_null_is_equivalent_to_leaving_parent(self):
        mg = ItemManager()
        child = mg.new("Child")
        parent = mg.new("Parent")
        parent.adopt(child)

        self.assertFalse(NullItem.is_parent_of(child))
        self.assertTrue(parent.is_parent_of(child))
        NullItem.adopt(child)
        self.assertTrue(NullItem.is_parent_of(child))
        self.assertFalse(parent.is_parent_of(child))

        
    def test_renaming(self):
        NullItem.rename("New Name")
        self.assertEqual(NullItem.name,"")
        NullItem._rename("New Name")
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

    def test_undo_passing_to_new_parent_when_child_name_was_adjusted(self):
        A_child = self.mg.new("Child")
        A_parent = self.mg.new("Parent 1")
        A_parent.adopt(A_child)

        B_child = self.mg.new("Child")
        B_parent = self.mg.new("Parent 2")
        B_parent.adopt(B_child)

        A_parent.pass_to_new_parent(A_child, B_parent)
        self.assertEqual(A_child.name, "Child (1)")

        self.mg.undo()
        self.assertEqual(A_child.name, "Child")
        self.mg.redo()
        self.assertEqual(A_child.name, "Child (1)")


class Test_Child_Copy(unittest.TestCase):

    def setUp(self) -> None:
        self.mg = ItemManager()
        self.parent = self.mg.new("Parent")
        self.child = self.mg.new("Child")
        self.parent.adopt(self.child)
        self.copy = self.child.get_copy()

    def test_child_copy_has_the_same_parent_as_the_original(self):
        self.assertTrue(self.parent.is_parent_of(self.copy))
        self.assertEqual(self.copy.parent, self.parent)
        self.assertEqual(self.copy.name, "Child (1)")

    def test_undo_and_redo_copying(self):
        self.mg.undo()
        self.assertFalse(self.parent.is_parent_of(self.copy))
        self.assertTrue(self.copy.parent, NullItem)
        self.assertEqual(self.copy.name, "Child")

        self.mg.redo()
        self.assertTrue(self.parent.is_parent_of(self.copy))
        self.assertEqual(self.copy.name, "Child (1)")

        self.mg.undo()
        self.assertFalse(self.parent.is_parent_of(self.copy))
        self.assertEqual(self.copy.name, "Child")


class Test_Undo_And_Redo_Multiple_Operations(unittest.TestCase):

    def test_copying_and_renaming(self):
        mg = ItemManager()
        parent = mg.new("Parent")
        child = mg.new("Child")
        parent.adopt(child)
        child_copy = child.get_copy()
        child_copy.rename("Second child")

        for _ in range(3):
            mg.undo()
            mg.undo()
            mg.undo()
            self.assertEqual(child_copy.parent,NullItem)
            self.assertFalse(parent.is_parent_of(child_copy))
            self.assertEqual(child_copy.name, "Child")
            self.assertEqual(child.parent, NullItem)
            self.assertFalse(parent.is_parent_of(child))
            mg.redo()
            self.assertEqual(child.parent, parent)
            self.assertTrue(parent.is_parent_of(child))
            self.assertEqual(child_copy.parent,NullItem)
            mg.redo()
            self.assertEqual(child_copy.parent,parent)
            self.assertEqual(child_copy.name, "Child (1)")
            mg.redo()
            self.assertEqual(child_copy.parent,parent)
            self.assertEqual(child_copy.name, "Second child")

    def test_undo_and_executing_new_command_erases_redo_command(self):
        mg = ItemManager()
        parent = mg.new("Parent")
        child = mg.new("Child")
        parent.adopt(child)
        child.rename("The Child")

        mg.undo()
        self.assertEqual(child.name, "Child")
        mg.redo()
        self.assertEqual(child.name, "The Child")
        mg.undo()
        child.rename("The First Child")
        mg.redo() # this redo has no effect
        self.assertEqual(child.name, "The First Child")
        mg.undo()
        self.assertEqual(child.name,"Child")
        mg.redo()
        self.assertEqual(child.name, "The First Child")


from src.cmd.commands import Command
from src.core.item import Adoption_Data
import dataclasses
class Test_Connecting_External_Commands_To_The_Adopt_Command(unittest.TestCase):

    @dataclasses.dataclass
    class AdoptionDisplay:
        notification:str = ""
        message:str = ""
        count:int = 0

    @dataclasses.dataclass
    class RecordAdoption(Command):
        parent:Item
        child:Item
        display:Test_Connecting_External_Commands_To_The_Adopt_Command.AdoptionDisplay
        old_message:str = dataclasses.field(init=False)
        new_message:str = dataclasses.field(init=False)
  
        def run(self)->None:
            self.old_message = self.display.message
            self.new_message = f"{self.parent.name} has adopted the {self.child.name}"
            self.display.message = self.new_message
            self.display.count += 1

        def undo(self)->None:
            self.display.count -= 1
            self.display.message = self.old_message

        def redo(self)->None: self.run()

 
    def setUp(self) -> None:
        self.display = self.AdoptionDisplay()
        self.mg = ItemManager()
        self.parent = self.mg.new("Parent")

        def record_adoption(data:Adoption_Data)->Command:
            return self.RecordAdoption(data.parent, data.child, self.display)

        self.parent.do_on_adoption(
            'test', 
            record_adoption
        ) 

    def test_adding_simple_command_to_the_adopt_command(self):
        child = self.mg.new("Child")
        self.parent.adopt(child)
        self.assertEqual(self.display.message, "Parent has adopted the Child")
        self.assertEqual(self.display.count, 1)

        self.mg.undo()
        self.assertEqual(self.display.message, "")
        self.assertEqual(self.display.count, 0)
        self.mg.redo()
        self.assertEqual(self.display.message, "Parent has adopted the Child")
        self.assertEqual(self.display.count, 1)
        self.mg.undo()
        self.assertEqual(self.display.message, "")
        self.assertEqual(self.display.count, 0)

    def test_adoption_of_two_children(self):
        child = self.mg.new("Child")
        self.parent.adopt(child)

        child2 = self.mg.new("Child 2")
        self.parent.adopt(child2)
        self.assertEqual(self.display.message, "Parent has adopted the Child 2")
        self.assertEqual(self.display.count, 2)

        self.mg.undo()
        self.assertEqual(self.display.message, "Parent has adopted the Child")
        self.assertEqual(self.display.count, 1)

        self.mg.undo()
        self.assertEqual(self.display.message, "")
        self.assertEqual(self.display.count, 0)



from src.core.item import Renaming_Data
class Test_Adding_External_Command_To_Renaming(unittest.TestCase):

    @dataclasses.dataclass
    class Label:
        text:str
    
    @dataclasses.dataclass
    class CatchNewItemNameInLabel(Command):
        label:Test_Adding_External_Command_To_Renaming.Label
        item:Item
        orig_text:str = dataclasses.field(init=False)
        new_text:str = dataclasses.field(init=False)

        def run(self)->None:
            self.orig_text = self.label.text
            self.label.text = self.item.name
            self.new_text = self.item.name

        def undo(self)->None:
            self.label.text = self.orig_text
        
        def redo(self)->None:
            self.label.text = self.new_text


    def setUp(self) -> None:
        self.label = Test_Adding_External_Command_To_Renaming.Label("Empty")
        self.mg = ItemManager()
        self.item = self.mg.new("Child")
        def catch_new_item_name_in_label(data:Renaming_Data)->self.CatchNewItemNameInLabel:
            return self.CatchNewItemNameInLabel(self.label, data.item)
        
        self.item.do_on_renaming(
            'test',
            catch_new_item_name_in_label
        )

    def test_single_rename_command_undo_and_redo(self):
        self.item.rename("The Child")
        self.assertEqual(self.label.text, "The Child")

        self.mg.undo()
        self.assertEqual(self.label.text, "Empty")
        self.mg.redo()
        self.assertEqual(self.label.text, "The Child")
        self.mg.undo()
        self.assertEqual(self.label.text, "Empty")


    def test_two_rename_commands_undo_and_redo(self):
        self.item.rename("The Child")
        self.item.rename("The Awesome Child")
        self.assertEqual(self.label.text, "The Awesome Child")

        self.mg.undo()
        self.mg.undo()
        self.assertEqual(self.label.text, "Empty")
        self.assertEqual(self.item.name, "Child")
        self.mg.undo() # does nothing
        self.assertEqual(self.label.text, "Empty")
        self.assertEqual(self.item.name, "Child")
        self.mg.redo()
        self.assertEqual(self.label.text, "The Child")
        self.assertEqual(self.item.name, "The Child")
        self.mg.redo()
        self.assertEqual(self.label.text, "The Awesome Child")
        self.assertEqual(self.item.name, "The Awesome Child")
 
    
        


if __name__=="__main__": unittest.main()







































