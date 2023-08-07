import sys 
sys.path.insert(1,"src")


import treeview 
from tree import Tree
import unittest
from typing import List
import tkinter.ttk as ttk
import tkinter as tk


class Test_Empty_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.load_tree(self.tree1)

    def test_adding_single_tree(self):
        self.assertEqual(self.view.trees, ("Tree 1",))
        self.view.load_tree(Tree("Tree 2"))
        self.assertEqual(self.view.trees, ("Tree 1", "Tree 2"))

    def test_adding_already_existing_tree_raises_exception(self):
        self.assertRaises(ValueError,self.view.load_tree,Tree("Tree 1"))

    def test_removing_tree(self):
        self.view.load_tree(Tree("Tree 2"))
        self.view.remove_tree("Tree 1")
        self.assertEqual(self.view.trees, ("Tree 2",))
        self.view.remove_tree("Tree 2")
        self.assertEqual(self.view.trees, tuple())

    def test_removing_nonexistent_tree_raises_exception(self):
        self.assertRaises(ValueError,self.view.remove_tree,"Nonexistent tree")
    
    def test_adding_branch_to_tree_adds_element_to_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.assertEqual(len(self.view.widget.get_children("Tree 1")), 1)
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children("Tree 1")[0])["text"],
            "Branch X",
        )
    
    def test_adding_branch_to_tree_branch_adds_element_to_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.add_branch("Small branch",{},"Branch X")
        self.assertEqual(len(self.view.widget.get_children("Tree 1")), 1)
        branch_x_iid = self.view.widget.get_children("Tree 1")[0]
        self.assertEqual(len(self.view.widget.get_children(branch_x_iid)), 1)

    def test_adding_branch_with_already_existing_name_makes_treeview_show_the_adjusted_name(self):
        self.tree1.add_branch("Branch X")
        self.tree1.add_branch("Branch X")
        adjusted_name = self.tree1._branches[-1].name
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children("Tree 1")[-1])["text"],
            adjusted_name
        )

    def test_removing_branch_from_tree_removes_element_from_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.remove_branch("Branch X")
        self.assertEqual(self.view.widget.get_children("Tree 1"), ())

    def test_removing_nonexistent_branch_does_not_alter_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.remove_branch("Nonexistent branch")
        self.assertEqual(len(self.view.widget.get_children("Tree 1")), 1)

    def test_renaming_branch_is_reflected_in_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.rename_branch(("Branch X",), "Branch Y")
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children("Tree 1")[-1])["text"],
            "Branch Y"
        )

    def test_renaming_nonexistent_branch_does_not_affect_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.rename_branch(("Branch XXXX",), "Branch Y")
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children("Tree 1")[-1])["text"],
            "Branch X"
        )

    def test_moving_branch_to_other_parent_is_reflected_in_the_treeview(self):
        self.tree1.add_branch("Branch X")
        self.tree1.add_branch("Branch to be moved")
        self.tree1.move_branch(("Branch to be moved",), ("Branch X",))
        self.assertEqual(len(self.view.widget.get_children("Tree 1")), 1)
        branch_x_iid = self.view.widget.get_children("Tree 1")[0]
        self.assertEqual(len(self.view.widget.get_children(branch_x_iid)), 1)


class Test_Accessing_Branch_From_Treeview(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.load_tree(self.tree1)

    def test_accessing_the_branch_associated_with_the_treeview_item(self):
        self.tree1.add_branch("Branch X")
        branch_x_iid = self.view.widget.get_children("Tree 1")[0]
        self.assertEqual(self.view.branch(branch_x_iid).name, "Branch X")

    def test_accessing_the_branch_with_nonexistent_iid_returns_none(self):
        self.tree1.add_branch("Branch X")
        nonexistent_iid = "Nonexistent iid"
        self.assertEqual(self.view.branch(nonexistent_iid), None)


class Test_Right_Click_Menu(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.load_tree(self.tree1)
        self.tree1.add_branch("Branch X", {"length":45})
        self.branch_x_iid = self.view.widget.get_children("Tree 1")[-1] 
        self.view._open_right_click_menu(self.branch_x_iid)

    def test_deleting_branch(self):
        self.assertListEqual(self.tree1.branches(),["Branch X"])
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_DELETE)
        self.assertListEqual(self.tree1.branches(),[])

    def test_right_clicking_again_outside_any_treeview_item_does_not_create_any_menu(self):
        ID_IF_NO_ITEM_CLICKED = ""
        self.view._open_right_click_menu(ID_IF_NO_ITEM_CLICKED)
        self.assertEqual(self.view.right_click_menu,None)
    
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
    
    def test_after_confirming_the_entries_the_edit_window_closes(self):
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_EDIT)
        self.view.confirm_edit_entry_values(self.branch_x_iid)
        self.assertEqual(self.view.edit_window,None)
        self.assertDictEqual(self.view.edit_entries,{})

    def test_after_disregarding_the_changes_the_edit_window_closes(self):
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_EDIT)
        self.view.disregard_edit_entry_values()
        self.assertEqual(self.view.edit_window,None)
        self.assertDictEqual(self.view.edit_entries,{})

    def test_bringing_back_original_entry_values_in_the_edit_window(self):
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_EDIT)
        self.view.edit_entries["name"].delete(0,"end")
        self.view.edit_entries["name"].insert(0,"Branch YZ")

        self.assertEqual(self.view.edit_entries["name"].get(),"Branch YZ")
        button_frame = self.view.edit_window.winfo_children()[1]
        revert_button:tk.Button = button_frame.winfo_children()[0]
        revert_button.invoke()
        self.assertEqual(self.view.edit_entries["name"].get(),"Branch X")

class Test_Moving_Branch_Under_New_Parent(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()
        self.tree1 = Tree("Tree 1")
        self.view.load_tree(self.tree1)
        self.tree1.add_branch("Branch X", {"length":45})
        self.tree1.add_branch("Branch Y", {"length":45})
        self.tree1.add_branch("Branch Z", {"length":20})
        self.tree1.add_branch("Child of Z", {"length":10}, "Branch Z")
        self.small_branch_id = self.view.widget.get_children("Tree 1")[-1] 
        self.view._open_right_click_menu(self.small_branch_id)
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_MOVE)
        
    def test_available_parents_do_not_include_branch_itself_nor_its_children(self):
        def get_descendant_names(treeview_widget:ttk.Treeview, item_id:str)->List[str]:
            descendants_names:List[str] = list()
            for child_id in treeview_widget.get_children(item_id):
                descendants_names.append(self.view._map[child_id].name)
                descendants_names.extend(get_descendant_names(treeview_widget,child_id))
            return descendants_names
        self.assertListEqual(get_descendant_names(self.view.available_parents,"Tree 1"), ["Branch X","Branch Y"])
        
    def test_move_branch_under_a_new_parent(self):
        self.view.available_parents.selection_set(self.tree1._find_branch("Branch X").data["treeview_iid"])
        ok_button:tk.Button = self.view.move_window.winfo_children()[-1].winfo_children()[0]
        ok_button.invoke()

        moved_branch = self.view._map[self.small_branch_id]
        self.assertEqual(moved_branch.parent.name,"Branch X")
        #test that move window closes after clicking the ok button
        self.assertEqual(self.view.move_window,None)
        #test that available parents are deleted after clicking the ok button
        self.assertEqual(self.view.available_parents,None)

    def test_selecting_a_new_parent_but_canceling_the_move_have_no_effect_on_the_tree(self):
        self.view.available_parents.selection_set(self.tree1._find_branch("Branch X").data["treeview_iid"])
        cancel_button:tk.Button = self.view.move_window.winfo_children()[-1].winfo_children()[1]
        cancel_button.invoke()

        moved_branch = self.view._map[self.small_branch_id]
        self.assertEqual(moved_branch.parent.name,"Tree 1")
        #test that move window closes after clicking the cancel button
        self.assertEqual(self.view.move_window,None)
        #test that available parents are deleted after clicking the cancel button
        self.assertEqual(self.view.available_parents,None)


class Test_Load_Existing_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.tree1 = Tree("Tree 1")
        self.tree1.add_branch("Branch X")
        self.tree1.add_branch("Child of X",{},"Branch X")
        self.tree1.add_branch("Branch Y")
        self.tree1.add_branch("Grandchild of X",{},"Branch X","Child of X")

    def test_loading_tree(self):
        view = treeview.Treeview()
        view.load_tree(self.tree1)
        main_branches_ids = view.widget.get_children("Tree 1")
        self.assertListEqual([view._map[id].name for id in main_branches_ids], ["Branch X","Branch Y"])
        branch_x_id = self.tree1._branches[0].data["treeview_iid"]
        child_of_x_id = view.widget.get_children(branch_x_id)[0]
        self.assertEqual(view.branch(child_of_x_id).name,"Child of X")
        grandchild_of_x_id = view.widget.get_children(child_of_x_id)[0]
        self.assertEqual(view.branch(grandchild_of_x_id).name,"Grandchild of X")


class Test_Adding_Branch_Via_Treeview(unittest.TestCase):

    def setUp(self) -> None:
        self.tree1 = Tree("Tree 1")
        self.view = treeview.Treeview()
        self.view.load_tree(self.tree1)
        self.view._open_right_click_menu("Tree 1",root=True)

    def test_adding_single_branch_to_the_tree(self):
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_ADD)
        self.view.add_window_entries["name"].delete(0,"end")
        self.view.add_window_entries["name"].insert(0,"Branch X")
        ok_button:tk.Button = self.view.add_window.winfo_children()[1].winfo_children()[0]
        ok_button.invoke()
        self.assertListEqual(self.tree1.branches(),["Branch X"])
        # add_window and add_window_entries are destroyed
        self.assertEqual(self.view.add_window,None)
        self.assertDictEqual(self.view.add_window_entries, {})
    
    def test_canceling_adding_of_a_new_branch(self):
        self.view.right_click_menu.invoke(treeview.MENU_CMD_BRANCH_ADD)
        self.view.add_window_entries["name"].delete(0,"end")
        self.view.add_window_entries["name"].insert(0,"Branch X")
        cancel_button:tk.Button = self.view.add_window.winfo_children()[1].winfo_children()[-1]
        cancel_button.invoke()
        self.assertListEqual(self.tree1.branches(),[])
        # add_window and add_window_entries are destroyed
        self.assertEqual(self.view.add_window,None)
        self.assertDictEqual(self.view.add_window_entries, {})


if __name__=="__main__": unittest.main()