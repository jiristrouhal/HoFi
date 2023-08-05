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
        branch_x_iid = self.view._widget.get_children("Tree 1")[0]
        self.assertEqual(len(self.view._widget.get_children(branch_x_iid)), 1)


class Test_Accessing_Branch_From_Treeview(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.add_tree_to_widget(self.tree1)

    def test_accessing_the_branch_associated_with_the_treeview_item(self):
        self.tree1.add_branch("Branch X")
        branch_x_iid = self.view._widget.get_children("Tree 1")[0]
        self.assertEqual(self.view.branch(branch_x_iid).name, "Branch X")

    def test_accessing_the_branch_with_nonexistent_iid_returns_none(self):
        self.tree1.add_branch("Branch X")
        nonexistent_iid = "Nonexistent iid"
        self.assertEqual(self.view.branch(nonexistent_iid), None)


class Test_Right_Click_Menu(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.add_tree_to_widget(self.tree1)
        self.tree1.add_branch("Branch X", {"length":45})
        self.branch_x_iid = self.view._widget.get_children("Tree 1")[-1] 
        self.view._open_right_click_menu_for_item(self.branch_x_iid)

    def test_deleting_branch(self):
        self.assertListEqual(self.tree1.branches(),["Branch X"])
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_DELETE)
        self.assertListEqual(self.tree1.branches(),[])
    
    def test_menu_is_destroyed_after_running_its_command(self):
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_DELETE)
        self.assertEqual(self.view.right_click_menu,None)

    def test_manually_changing_tkinter_entries_and_confirming_choice_rewrites_branch_attributes(self):
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_EDIT)

        self.view.edit_entries["name"].delete(0,"end")
        self.view.edit_entries["name"].insert(0,"Branch YZ")
        self.view.edit_entries["length"].delete(0,"end")
        self.view.edit_entries["length"].insert(0,"78")

        self.view.confirm_edit_entry_values(self.branch_x_iid)
        self.assertEqual(self.tree1.branches()[0],"Branch YZ")
        self.assertEqual(self.tree1._branches[0].attributes["length"],"78")


if __name__=="__main__": unittest.main()