import sys 
sys.path.insert(1,"src")


import treeview 
from tree import Tree
import unittest


class Test_Empty_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.add_tree(self.tree1)

    def test_adding_single_tree(self):
        self.assertEqual(self.view.trees, ("Tree 1",))
        self.view.add_tree(Tree("Tree 2"))
        self.assertEqual(self.view.trees, ("Tree 1", "Tree 2"))

    def test_adding_already_existing_tree_raises_exception(self):
        self.assertRaises(ValueError,self.view.add_tree,Tree("Tree 1"))

    def test_removing_tree(self):
        self.view.add_tree(Tree("Tree 2"))
        self.view.remove_tree("Tree 1")
        self.assertEqual(self.view.trees, ("Tree 2",))
        self.view.remove_tree("Tree 2")
        self.assertEqual(self.view.trees, tuple())

    def test_removing_nonexistent_tree_raises_exception(self):
        self.assertRaises(ValueError,self.view.remove_tree,"Nonexistent tree")
    
    def test_adding_branch_to_tree_adds_element_to_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.assertEqual(len(self.view._widget.get_children("Tree 1")), 1)
        self.assertEqual(
            self.view._widget.item(self.view._widget.get_children("Tree 1")[0])["text"],
            "Branch X",
        )
    
    def test_adding_branch_to_tree_branch_adds_element_to_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.add_branch("Small branch",{},"Branch X")
        self.assertEqual(len(self.view._widget.get_children("Tree 1")), 1)
        branch_x_iid = self.view._widget.get_children("Tree 1")[0]
        self.assertEqual(len(self.view._widget.get_children(branch_x_iid)), 1)

    def test_removing_branch_from_tree_removes_element_from_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.remove_branch("Branch X")
        self.assertEqual(self.view._widget.get_children("Tree 1"), ())
        

if __name__=="__main__": unittest.main()