import sys 
sys.path.insert(1,"src")

import unittest
from typing import List
import tkinter.ttk as ttk
import tkinter as tk


import controls.tree_editor  as tree_editor
from core.tree import Tree, TreeItem, tt


class Test_Creating_Trees(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.view = tree_editor.TreeEditor()
        self.tree1 = Tree("Tree 1",tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        self.view.load_tree(self.tree1)
        # prevent all GUI elements from showing up
        self.view._messageboxes_allowed = False

    def test_adding_single_tree(self):
        self.assertEqual(self.view.trees, ("Tree 1",))
        self.view.load_tree(Tree("Tree 2",tag="Tree"))
        self.assertEqual(self.view.trees, ("Tree 2", "Tree 1"))
        self.assertTrue(self.view.is_tree(self.view._map[self.view.widget.get_children()[0]]))

    def test_adding_already_existing_tree_raises_exception(self):
        self.assertRaises(ValueError,self.view.load_tree,Tree("Tree 1",tag="Tree"))

    def test_removing_tree(self):
        tree2 = Tree("Tree 2",tag="Tree")
        tree2_iid = str(id(tree2))
        tree2.new("Branch X", tag="Branch")
        def action(x): # pragma: no cover
            pass 
        tree2.add_action(self.view.label,'on_removal',action)
        tree2._children[-1].add_action(self.view.label,'on_removal',action)
        self.view.load_tree(tree2)
        self.view.remove_tree(self.tree1_iid)
        self.assertEqual(self.view.trees, ("Tree 2",))
        self.view.remove_tree(tree2_iid)
        self.assertEqual(self.view.trees, tuple())

    def test_removing_nonexistent_tree_raises_exception(self):
        self.assertRaises(ValueError,self.view.remove_tree,"Nonexistent tree")
    
    def test_adding_branch_to_tree_adds_element_to_the_treeview(self):
        self.tree1.new("Branch X",tag='Branch')
        self.assertEqual(len(self.view.widget.get_children(self.tree1_iid)), 1)
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children(self.tree1_iid)[0])["text"],
            "Branch X",
        )
    
    def test_adding_branch_to_tree_branch_adds_element_to_the_treeview(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.new("Small branch","Branch X",tag='Branch')
        self.assertEqual(len(self.view.widget.get_children(self.tree1_iid)), 1)
        branch_x_iid = self.view.widget.get_children(self.tree1_iid)[0]
        self.assertEqual(len(self.view.widget.get_children(branch_x_iid)), 1)

    def test_adding_branch_with_already_existing_name_makes_treeview_show_the_adjusted_name(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.new("Branch X",tag='Branch')
        adjusted_name = self.tree1._children[-1].name
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children(self.tree1_iid)[0])["text"],
            adjusted_name
        )

    def test_removing_branch_from_tree_removes_element_from_the_treeview(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.remove_child("Branch X")
        self.assertEqual(self.view.widget.get_children(self.tree1_iid), ())

    def test_removing_nonexistent_branch_does_not_alter_the_treeview(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.remove_child("Nonexistent branch")
        self.assertEqual(len(self.view.widget.get_children(self.tree1_iid)), 1)

    def test_renaming_branch_is_reflected_in_the_treeview(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.rename_child(("Branch X",), "Branch Y")
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children(self.tree1_iid)[0])["text"],
            "Branch Y"
        )

    def test_renaming_nonexistent_branch_does_not_affect_the_treeview(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.rename_child(("Branch XXXX",), "Branch Y")
        self.assertEqual(
            self.view.widget.item(self.view.widget.get_children(self.tree1_iid)[0])["text"],
            "Branch X"
        )

    def test_moving_branch_to_other_parent_is_reflected_in_the_treeview(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.new("Branch to be moved",tag='Branch')
        self.tree1.move_child(("Branch to be moved",), ("Branch X",))
        self.assertEqual(len(self.view.widget.get_children(self.tree1_iid)), 1)
        branch_x_iid = self.view.widget.get_children(self.tree1_iid)[0]
        self.assertEqual(len(self.view.widget.get_children(branch_x_iid)), 1)

    

class Test_Accessing_Branch_From_Treeview(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.view = tree_editor.TreeEditor()
        self.tree1 = Tree("Tree 1",tag='Tree')
        self.view.load_tree(self.tree1)
        # prevent all GUI elements from showing up
        self.view._messageboxes_allowed = False

    def test_accessing_the_branch_associated_with_the_treeview_item(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1_iid = str(id(self.tree1))
        branch_x_iid = self.view.widget.get_children(self.tree1_iid)[0]
        self.assertEqual(self.view.tree_item(branch_x_iid).name, "Branch X")

    def test_accessing_the_branch_with_nonexistent_iid_returns_none(self):
        self.tree1.new("Branch X",tag='Branch')
        nonexistent_iid = "Nonexistent iid"
        self.assertEqual(self.view.tree_item(nonexistent_iid), None)

class Test_Right_Click_Menu(unittest.TestCase):

    def setUp(self) -> None:

        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New", "weight":500},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New","length":10},children=('Branch',)),
        )
        self.view = tree_editor.TreeEditor()
        self.tree1 = Tree("Tree 1",tag='Branch')
        self.tree1_iid = str(id(self.tree1))
        # prevent all GUI elements from showing up
        self.view._messageboxes_allowed = False
        self.view.load_tree(self.tree1)
        self.tree1.new("Branch X",tag='Branch')
        self.branch_x_iid = self.view.widget.get_children(self.tree1_iid)[-1] 
        self.branchx = self.view._map[self.branch_x_iid ]
        self.view.open_right_click_menu(self.branch_x_iid)

    def test_adding_branch_via_right_click_menu(self):
        self.view.right_click_menu.invoke(tree_editor._define_add_cmd_label('Branch'))
        self.assertTrue(self.view.add_window.winfo_exists())
        self.view.entries["name"].delete(0,"end")
        self.view.entries["name"].insert(0,"Child of X")
        self.view.confirm_add_entry_values(self.branchx, tag="Branch")

    def test_deleting_branch(self):
        self.assertListEqual(self.tree1.children(),["Branch X"])
        self.view.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_DELETE)
        self.assertListEqual(self.tree1.children(),[])

    def test_right_clicking_again_outside_any_treeview_item_does_not_create_any_menu(self):
        ID_IF_NO_ITEM_CLICKED = ""
        self.view.open_right_click_menu(ID_IF_NO_ITEM_CLICKED)
        self.assertFalse(self.view.right_click_menu.winfo_exists())
    
    def test_menu_is_destroyed_after_running_its_command(self):
        self.view.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_DELETE)
        self.assertFalse(self.view.right_click_menu.winfo_exists())

    def test_manually_changing_tkinter_entries_and_confirming_choice_rewrites_branch_attributes(self):
        self.view.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_EDIT)

        self.view.entries["name"].delete(0,"end")
        self.view.entries["name"].insert(0,"Branch YZ")
        self.view.entries["length"].delete(0,"end")
        self.view.entries["length"].insert(0,78)

        self.view.confirm_edit_entry_values(self.branch_x_iid)
        self.assertEqual(self.tree1.children()[0],"Branch YZ")
        self.assertEqual(self.tree1._children[0].attributes["length"].value,78)
    
    def test_after_confirming_the_entries_the_edit_window_closes(self):
        self.view.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_EDIT)
        self.view.confirm_edit_entry_values(self.branch_x_iid)
        self.assertFalse(self.view.edit_window.winfo_exists())
        self.assertDictEqual(self.view.entries,{})

    def test_after_disregarding_the_changes_the_edit_window_closes(self):
        self.view.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_EDIT)
        self.view.disregard_edit_entry_values()
        self.assertFalse(self.view.edit_window.winfo_exists())
        self.assertDictEqual(self.view.entries,{})

    def test_bringing_back_original_entry_values_in_the_edit_window(self):
        self.view.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_EDIT)
        self.view.entries["name"].delete(0,"end")
        self.view.entries["name"].insert(0,"Branch YZ")

        self.assertEqual(self.view.entries["name"].get(),"Branch YZ")
        button_frame = self.view.edit_window.winfo_children()[1]
        revert_button:tk.Button = button_frame.winfo_children()[0]
        revert_button.invoke()
        self.assertEqual(self.view.entries["name"].get(),"Branch X")

class Test_Moving_Branch_Under_New_Parent(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )

        self.view = tree_editor.TreeEditor()
        self.tree1 = Tree("Tree 1",tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        # prevent all GUI elements from showing up
        self.view._messageboxes_allowed = False
        self.view.load_tree(self.tree1)
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.new("Branch Y",tag='Branch')
        self.tree1.new("Branch Z",tag='Branch')
        self.tree1.new("Child of Z","Branch Z", tag='Branch')
        self.small_branch_id = self.view.widget.get_children(self.tree1_iid)[0] 
        self.view.open_right_click_menu(self.small_branch_id)
        self.view.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_MOVE)
        
    def test_available_parents_do_not_include_branch_itself_nor_its_children(self):
        def get_descendant_names(treeview_widget:ttk.Treeview, item_id:str)->List[str]:
            descendants_names:List[str] = list()
            for child_id in treeview_widget.get_children(item_id):
                descendants_names.append(self.view._map[child_id].name)
                descendants_names.extend(get_descendant_names(treeview_widget,child_id))
            return descendants_names
        self.assertListEqual(get_descendant_names(self.view.available_parents,self.tree1_iid), ["Branch X","Branch Y"])
        
    def test_if_available_parents_are_destroyed_then_confirming_parent_has_no_effect(self):
        self.view.available_parents.destroy()
        ok_button:tk.Button = self.view.move_window.winfo_children()[-1].winfo_children()[0]
        ok_button.invoke()

    def test_confirming_moving_item_under_new_parent_has_no_effect_if_no_parent_is_selected_from_available_parents(self):
        self.view.available_parents.selection_clear()
        ok_button:tk.Button = self.view.move_window.winfo_children()[-1].winfo_children()[0]
        ok_button.invoke()
        
    def test_move_branch_under_a_new_parent(self):
        self.view.available_parents.selection_set(self.tree1._find_child("Branch X").data["treeview_iid"])
        ok_button:tk.Button = self.view.move_window.winfo_children()[-1].winfo_children()[0]
        ok_button.invoke()

        moved_branch = self.view._map[self.small_branch_id]
        self.assertEqual(moved_branch.parent.name,"Branch X")
        #test that move window closes after clicking the ok button
        self.assertFalse(self.view.move_window.winfo_exists())
        #test that available parents are deleted after clicking the ok button
        self.assertFalse(self.view.available_parents.winfo_exists())

    def test_selecting_a_new_parent_but_cancelling_the_move_has_no_effect_on_the_tree(self):
        
        self.view.available_parents.selection_set(self.tree1._find_child("Branch X").data["treeview_iid"])
        cancel_button:tk.Button = self.view.move_window.winfo_children()[-1].winfo_children()[1]
        cancel_button.invoke()

        moved_branch = self.view._map[self.small_branch_id]
        self.assertEqual(moved_branch.parent.name,"Tree 1")
        #test that move window closes after clicking the cancel button
        self.assertFalse(self.view.move_window.winfo_exists())
        #test that available parents are deleted after clicking the cancel button
        self.assertFalse(self.view.available_parents.winfo_exists())

    def test_selecting_no_parent_has_no_effect_on_the_tree(self):
        
        self.view.available_parents.selection_set()
        ok_button:tk.Button = self.view.move_window.winfo_children()[-1].winfo_children()[0]
        ok_button.invoke()

        moved_branch = self.view._map[self.small_branch_id]
        self.assertEqual(moved_branch.parent.name,"Tree 1")
        #test that move window closes after clicking the cancel button
        self.assertFalse(self.view.move_window.winfo_exists())
        #test that available parents are deleted after clicking the cancel button
        self.assertFalse(self.view.available_parents.winfo_exists())


class Test_Moving_Tree(unittest.TestCase):
    
    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.tree1 = Tree("Tree 1",tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        self.view = tree_editor.TreeEditor()
        self.view.load_tree(self.tree1)
    
    def test_available_parents_for_tree_are_always_none(self):
        self.view.open_move_window(self.tree1_iid)
        self.assertEqual(self.view.available_parents.get_children(),())


class Test_Load_Existing_Tree(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.tree1 = Tree("Tree 1",tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.new("Child of X","Branch X",tag='Branch')
        self.tree1.new("Branch Y",tag='Branch')
        self.tree1.new("Grandchild of X","Branch X","Child of X",tag='Branch')

    def test_loading_tree(self):
        view = tree_editor.TreeEditor()
        view.load_tree(self.tree1)
        main_branches_ids = view.widget.get_children(self.tree1_iid)
        self.assertListEqual(
            [view._map[id].name for id in main_branches_ids], 
            ["Branch Y","Branch X"]
        )
        branch_x_id = self.tree1._children[0].data["treeview_iid"]
        child_of_x_id = view.widget.get_children(branch_x_id)[0]
        self.assertEqual(view.tree_item(child_of_x_id).name,"Child of X")
        grandchild_of_x_id = view.widget.get_children(child_of_x_id)[0]
        self.assertEqual(view.tree_item(grandchild_of_x_id).name,"Grandchild of X")


class Test_Adding_Branch_Via_Treeview(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.tree1 = Tree("Tree 1",tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        self.view = tree_editor.TreeEditor()
        self.view.load_tree(self.tree1)
        self.view.open_right_click_menu(self.tree1_iid, root=True)
        self.assertTrue(self.view.right_click_menu.winfo_exists())
        # prevent all GUI elements from showing up
        self.view._messageboxes_allowed = False

    def test_adding_single_branch_to_the_tree(self):
        self.view.right_click_menu.invoke(tree_editor._define_add_cmd_label("Branch"))
        self.view.entries["name"].delete(0,"end")
        self.view.entries["name"].insert(0,"Branch X")
        ok_button:tk.Button = self.view.add_window.winfo_children()[1].winfo_children()[0]
        ok_button.invoke()
        self.assertListEqual(self.tree1.children(),["Branch X"])
        # add_window and add_window_entries are destroyed
        self.assertFalse(self.view.add_window.winfo_exists())
        self.assertDictEqual(self.view.entries, {})
    
    def test_canceling_adding_of_a_new_branch(self):
        self.view.right_click_menu.invoke(tree_editor._define_add_cmd_label("Branch"))
        self.view.entries["name"].delete(0,"end")
        self.view.entries["name"].insert(0,"Branch X")
        cancel_button:tk.Button = self.view.add_window.winfo_children()[1].winfo_children()[-1]
        cancel_button.invoke()
        self.assertListEqual(self.tree1.children(),[])
        # add_window and add_window_entries are destroyed
        self.assertFalse(self.view.add_window.winfo_exists())
        self.assertDictEqual(self.view.entries, {})


class Test_Modifying_Loaded_Tree(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.tree1 = Tree("Tree 1",tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        self.tree1.new("Branch X",tag='Branch')

        self.view = tree_editor.TreeEditor()
        self.view.load_tree(self.tree1)
        # prevent all GUI elements from showing up
        self.view._messageboxes_allowed = False
    
    def test_adding_child_to_branch_x(self):
        branch_x_id = self.view.widget.get_children(self.tree1_iid)[0]
        self.view.open_right_click_menu(branch_x_id)
        self.view.right_click_menu.invoke(tree_editor._define_add_cmd_label("Branch"))
        self.view.entries["name"].delete(0,"end")
        self.view.entries["name"].insert(0,"Child of X")
        self.view.add_window.winfo_children()[1].winfo_children()[0].invoke()
        self.assertEqual(self.view._map[self.view.widget.get_children(branch_x_id)[0]].name,"Child of X")


class Test_Error_Message(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.tree1 = Tree("Tree 1",tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        self.tree1.new("Branch with children",tag='Branch')
        self.tree1.new("Child","Branch with children",tag='Branch')
        self.view = tree_editor.TreeEditor()
        self.view.load_tree(self.tree1)
        # prevent all GUI elements from showing up
        self.view._messageboxes_allowed = False

    def test_pop_up_error_message_when_attempting_to_delete_branch_with_children(self):
        self.x = 0
        def set_x_to_one(*args): self.x=1
        self.tree1._find_child("Branch with children").do_if_error_occurs(
            'cannot_remove_branch_with_children',
            set_x_to_one
        )
        self.tree1.remove_child("Branch with children")
        self.assertEqual(self.x,1)


class Test_Actions_On_Selection(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.tree1 = Tree("Tree 1", tag="Tree")
        self.tree1_iid = str(id(self.tree1))
        self.view = tree_editor.TreeEditor()
        self.view.load_tree(self.tree1)
        self.view._messageboxes_allowed = False

    def test_selection_of_item_runs_the_action(self)->None:
        self.selection = ""
        def action(item:TreeItem)->None:
            self.selection = item.name
        self.view.add_action('Test','selection',action)
        self.view.widget.selection_set(self.tree1_iid)
        self.view.check_selection_changes()
        self.assertEqual(self.selection, "Tree 1")

    def test_repeated_selection_has_no_effect(self)->None:
        self.i = 0
        def action(item:TreeItem)->None:
            self.i += 1

        self.view.add_action('Test','selection',action)

        self.view.widget.selection_set(self.tree1_iid)
        # this function is automatically run when user click in Treeview
        self.view.check_selection_changes()
        self.view.check_selection_changes()
        self.assertEqual(self.i, 1)

        # the selection has to be first cleared and then repeated
        self.view.widget.selection_set()
        self.view.check_selection_changes()
        self.view.widget.selection_set(self.tree1_iid)
        self.view.check_selection_changes()
        self.assertEqual(self.i, 2)


class Test_Action_On_Item_Edit_Confirmation(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New","weight":50},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"New"},children=('Branch',)),
        )
        self.tree1 = Tree("Tree 1",tag='Tree')
        self.tree1_iid = str(id(self.tree1))
        self.view = tree_editor.TreeEditor()
        self.view.load_tree(self.tree1)
        self.view._messageboxes_allowed = False

    def test_edit_confirmation_runs_action(self)->None:
        self.w = self.tree1.attributes["weight"].value
        def action(item:TreeItem)->None:
            self.w = item.attributes["weight"].value

        self.view.add_action('Test','edit',action)
        self.assertEqual(self.w, 50)
        self.view.open_edit_window(self.tree1_iid)
        self.view.entries["weight"].delete(0,"end")
        self.view.entries["weight"].insert(0,75)
        self.view.confirm_edit_entry_values(self.tree1_iid)
        self.assertEqual(self.w, 75)

    def test_edit_cancellation_does_not_run_action(self)->None:
        self.w = self.tree1.attributes["weight"].value
        def action(item:TreeItem)->None: # pragma: no cover
            self.w = item.attributes["weight"].value

        self.view.add_action('Test','edit',action)
        self.assertEqual(self.w, 50)
        self.view.open_edit_window(self.tree1_iid)
        self.view.entries["weight"].delete(0,"end")
        self.view.entries["weight"].insert(0,75)
        self.view.disregard_edit_entry_values()
        self.assertEqual(self.w, 50)


class Test_Loading_Item_With_Icon_Defined_By_Template(unittest.TestCase):

    def test_loading_item_with_image_in_template(self) -> None:

        tt.clear()
        image = ""
        tt.add(
            tt.NewTemplate('Tree',{"name":"New","weight":50},children=(), icon_file=image),
        )
        self.tree1 = Tree("Tree 1",tag='Tree')
        self.view = tree_editor.TreeEditor()
        self.view.load_tree(self.tree1)
    

class Test_User_Defined_Command_In_Right_Click_Menu(unittest.TestCase):

    def test_making_the_command_increment_some_integer(self):

        self.x = 0 
        def user_def_command(tree:Tree)->None:
            self.x += 1

        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"New"},children=(),user_def_cmds={"Increment x":user_def_command}),
        )
        
        editor = tree_editor.TreeEditor()
        tree = Tree("TreeA", tag="Tree")
        editor.load_tree(tree)
        editor.open_right_click_menu(tree.data["treeview_iid"])
        editor.right_click_menu.invoke("Increment x")
        self.assertEqual(self.x, 1)


class Test_Undo_Redo(unittest.TestCase):

    def setUp(self) -> None:
        tt.clear()
        tt.add(
            tt.NewTemplate('Tree',{"name":"Tree"},children=('Branch',)),
            tt.NewTemplate('Branch',{"name":"Branch XYZ"},children=('Branch',)),
        )
        self.editor = tree_editor.TreeEditor()
        self.treeA = Tree("TreeA",tag="Tree")
        self.editor.load_tree(self.treeA)
        self.treeA.new("Branch B",tag="Branch")
        self.branchB = self.treeA._children[0]
        self.branchB.new("Child of B", tag='Branch')
        self.childOfB = self.branchB._children[0]

        self.treeA_iid = self.treeA.data["treeview_iid"]

    def test_undo_and_redo_adding_new_item(self)->None:
        orig_map = self.editor._map.copy()

        self.editor.open_right_click_menu(self.treeA_iid)
        self.editor.right_click_menu.invoke(tree_editor._define_add_cmd_label("Branch"))
        self.editor.confirm_add_entry_values(self.treeA, tag = "Branch")
        self.editor.open_right_click_menu(self.treeA_iid)

        self.editor.right_click_menu.invoke(tree_editor._define_add_cmd_label("Branch"))
        self.editor.entries["name"].delete(0,"end")
        self.editor.entries["name"].insert(0,"Branch UVW")
        self.editor.confirm_add_entry_values(self.treeA, tag = "Branch")

        map_after_additions = self.editor._map.copy()

        branches = self.treeA.children()
        self.editor.undo(self.treeA_iid)
        self.editor.undo(self.treeA_iid)
        map_after_undos = self.editor._map.copy()
        branches_after_two_undos = self.treeA.children()
        self.editor.redo(self.treeA_iid)
        self.editor.redo(self.treeA_iid)
        map_after_redos = self.editor._map.copy()
        branches_after_two_redos = self.treeA.children()
        self.editor.undo(self.treeA_iid)
        self.editor.undo(self.treeA_iid)
        branches_after_two_repeated_undos = self.treeA.children()

        self.assertDictEqual(orig_map, map_after_undos)
        self.assertDictEqual(map_after_additions, map_after_redos)

        self.assertListEqual(branches, ["Branch B", "Branch XYZ", "Branch UVW"])
        self.assertListEqual(branches_after_two_undos, ["Branch B"])
        self.assertListEqual(branches_after_two_redos, ["Branch B", "Branch XYZ", "Branch UVW"])
        self.assertListEqual(branches_after_two_repeated_undos, ["Branch B"])
        
        
    def test_undo_and_redo_editing_item(self):
        self.editor.open_right_click_menu(self.branchB.data["treeview_iid"])
        self.editor.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_EDIT)

        orig_name = self.branchB.name

        self.editor.entries["name"].delete(0,"end")
        self.editor.entries["name"].insert(0,"Branch BB")
        self.editor.confirm_edit_entry_values(self.branchB.data["treeview_iid"])

        new_name = self.branchB.name
        self.editor.undo(self.branchB.data["treeview_iid"])
        name_after_undo = self.branchB.name
        self.editor.redo(self.branchB.data["treeview_iid"])
        name_after_redo = self.branchB.name
        self.editor.undo(self.branchB.data["treeview_iid"])
        name_after_second_undo = self.branchB.name

        self.assertEqual(orig_name,"Branch B")
        self.assertEqual(new_name,"Branch BB")
        self.assertEqual(name_after_undo,"Branch B")
        self.assertEqual(name_after_redo, "Branch BB")
        self.assertEqual(name_after_second_undo, "Branch B")

    def test_undo_and_redo_moving_item(self):
        self.editor.open_right_click_menu(self.childOfB.data["treeview_iid"])
        self.editor.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_MOVE)
        self.editor.available_parents.selection_set(self.treeA.data["treeview_iid"])
        self.editor.confirm_parent(self.childOfB.data["treeview_iid"])

        new_parent = self.childOfB.parent.name
        self.editor.undo(self.treeA_iid)       
        parent_after_undo = self.childOfB.parent.name
        self.editor.redo(self.treeA_iid)
        parent_after_redo = self.childOfB.parent.name
        self.editor.undo(self.treeA_iid)       
        parent_after_second_undo = self.childOfB.parent.name

        self.assertEqual(new_parent,"TreeA")
        self.assertEqual(parent_after_undo,"Branch B")
        self.assertEqual(parent_after_redo,"TreeA")
        self.assertEqual(parent_after_second_undo,"Branch B")

    def test_undo_and_redo_removing_item(self)->None:
        self.editor.open_right_click_menu(self.childOfB.data["treeview_iid"])
        self.editor.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_DELETE)
        
        children = self.branchB.children()
        self.editor.undo(self.treeA_iid)
        children_after_undo = self.branchB.children()
        self.editor.redo(self.treeA_iid)
        children_after_redo = self.branchB.children()
        self.editor.undo(self.treeA_iid)
        children_after_second_undo = self.branchB.children()

        self.assertListEqual(children, [])
        self.assertListEqual(children_after_undo, ["Child of B"])
        self.assertListEqual(children_after_redo, [])
        self.assertListEqual(children_after_second_undo, ["Child of B"])

    def test_undo_and_redo_renaming_and_removal(self)->None:
        self.editor.open_right_click_menu(self.childOfB.data["treeview_iid"])
        self.editor.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_EDIT)
        self.editor.entries["name"].delete(0,"end")
        self.editor.entries["name"].insert(0,"New name for Child of B")
        self.editor.confirm_edit_entry_values(self.childOfB.data["treeview_iid"])
        
        self.editor.open_right_click_menu(self.childOfB.data["treeview_iid"])
        self.editor.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_DELETE)

        self.assertListEqual(self.branchB.children(),[])
        self.editor.undo(self.treeA_iid)
        self.assertListEqual(self.branchB.children(),["New name for Child of B"])
        self.editor.undo(self.treeA_iid)
        self.assertListEqual(self.branchB.children(),["Child of B"])
        # the undo stack is now empty and so, further undo's have no effect
        self.editor.undo(self.treeA_iid)
        self.assertListEqual(self.branchB.children(),["Child of B"])

        self.editor.redo(self.treeA_iid)
        self.editor.redo(self.treeA_iid)
        self.assertListEqual(self.branchB.children(),[])

    def test_undo_can_be_done_even_after_unloading_the_tree_and_loading_it_again(self):
        self.editor.open_right_click_menu(self.childOfB.data["treeview_iid"])
        self.editor.right_click_menu.invoke(tree_editor.MENU_CMD_BRANCH_DELETE)
        self.editor.remove_tree(self.treeA.data["treeview_iid"])

        self.editor.load_tree(self.treeA)
  
        children_of_B_after_loading = self.branchB.children()
        self.editor.undo(self.treeA_iid)
        children_of_B_after_undo = self.branchB.children()

        self.assertListEqual(children_of_B_after_loading, [])
        self.assertListEqual(children_of_B_after_undo, ["Child of B"])





if __name__=="__main__": unittest.main()