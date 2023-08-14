import sys
sys.path.insert(1,"src")


import src.treelist as tlist
import unittest
from tree import Tree


class Test_Modifying_List(unittest.TestCase):

    def setUp(self) -> None:
        self.nlist = tlist.TreeList()
    
    def test_adding_to_list(self)->None:
        self.nlist.append(Tree("Item 1"))
        self.nlist.append(Tree("Item 2"))
        self.assertListEqual(self.nlist.names, ["Item 1", "Item 2"])

    def test_removing_from_list(self)->None:
        self.nlist.append(Tree("Item 1"))
        self.nlist.append(Tree("Item 2"))
        self.nlist.remove("Item 1")
        self.assertListEqual(self.nlist.names, ["Item 2"])

    def test_removing_nonexistent_item_has_no_effect(self)->None:
        self.nlist.append(Tree("Item X"))
        self.nlist.remove("Nonexistent item")
        self.assertListEqual(self.nlist.names, ["Item X"])

    def test_adding_item_with_already_existing_name_makes_the_new_tree_name_to_adjust(self):
        self.nlist.append(Tree("Item X"))
        self.nlist.append(Tree("Item X"))
        self.assertListEqual(self.nlist.names, ["Item X", "Item X (1)"])

    def test_action_on_adding_tree(self):
        self.x = ""
        def action(item:Tree): 
            self.x = "Item " + item.name + " was added."
        self.nlist.add_action_on_adding(action)
        self.nlist.append(Tree("XYZ"))
        self.assertEqual(self.x,  "Item XYZ was added.")

    def test_action_on_removal(self):
        self.x = ""
        item = Tree("XYZ")
        def action(item:Tree): 
            self.x = "Item " + item.name + " was removed."
        
        self.nlist.add_action_on_removal(action)
        self.nlist.append(item)
        self.nlist.remove("XYZ")
        self.assertEqual(self.x,  "Item XYZ was removed.")

    def test_action_on_renaming(self):
        self.name = "Foo"
        def action(item:Tree):
            self.name = "Wee"
        
        self.nlist.add_action_on_renaming(action)
        self.nlist.append(Tree("Thing"))
        self.nlist.rename("Thing", "It")
        self.assertEqual(self.name, "Wee")

if __name__=="__main__": unittest.main()