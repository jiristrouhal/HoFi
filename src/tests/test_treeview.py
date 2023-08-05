import sys 
sys.path.insert(1,"src")


import treeview 
from tree import Tree
import unittest


class Test_Empty_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.add_tree_to_widget(self.tree1)

    def test_adding_single_tree(self):
        self.assertEqual(self.view.trees, ("Tree 1",))
        self.view.add_tree_to_widget(Tree("Tree 2"))
        self.assertEqual(self.view.trees, ("Tree 1", "Tree 2"))

    def test_adding_already_existing_tree_raises_exception(self):
        self.assertRaises(ValueError,self.view.add_tree_to_widget,Tree("Tree 1"))

    def test_removing_tree(self):
        self.view.add_tree_to_widget(Tree("Tree 2"))
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

    def test_adding_branch_with_already_existing_name_makes_treeview_show_the_adjusted_name(self):
        self.tree1.add_branch("Branch X")
        self.tree1.add_branch("Branch X")
        adjusted_name = self.tree1._branches[-1].name
        self.assertEqual(
            self.view._widget.item(self.view._widget.get_children("Tree 1")[-1])["text"],
            adjusted_name
        )

    def test_removing_branch_from_tree_removes_element_from_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.remove_branch("Branch X")
        self.assertEqual(self.view._widget.get_children("Tree 1"), ())

    def test_removing_nonexistent_branch_does_not_alter_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.remove_branch("Nonexistent branch")
        self.assertEqual(len(self.view._widget.get_children("Tree 1")), 1)

    def test_renaming_branch_is_reflected_in_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.rename_branch(("Branch X",), "Branch Y")
        self.assertEqual(
            self.view._widget.item(self.view._widget.get_children("Tree 1")[-1])["text"],
            "Branch Y"
        )

    def test_renaming_nonexistent_branch_does_not_affect_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.rename_branch(("Branch XXXX",), "Branch Y")
        self.assertEqual(
            self.view._widget.item(self.view._widget.get_children("Tree 1")[-1])["text"],
            "Branch X"
        )

    def test_moving_branch_to_other_parent_is_reflected_in_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.add_branch("Branch to be moved")
        self.tree1.move_branch(("Branch to be moved",), ("Branch X",))
        self.assertEqual(len(self.view._widget.get_children("Tree 1")), 1)
        branch_x_iid = self.view._widget.get_children("Tree 1")
        self.assertEqual(len(self.view._widget.get_children(branch_x_iid)), 1)
        

if __name__=="__main__": unittest.main()