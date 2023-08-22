import sys
sys.path.insert(1,"src")

import unittest
import controls.treemanager as tmg
import controls.treelist as treelist
import os
import core.tree as treemod


class Tree_Manager(tmg.Tree_Manager):

    def __init__(self,*args,**kwargs)->None:
        super().__init__(*args,**kwargs)
        self.xml_file_path = ""
        self.agree_with_renaming = False
        self.agree_with_removal = False
        self.file_already_in_use_error_msg = ""

    # override methods using messageboxes and filedialogs not suitable for unit testing
    def _get_filepath(self)->str:
        return self.xml_file_path
    
    def _ask_for_directory(self) -> str:
        return os.path.dirname(self.xml_file_path)
    
    def _confirm_renaming_if_exported_file_already_exists(self, name: str) -> bool:
        return self.agree_with_renaming
    
    def _removal_confirmed(self, name: str) -> bool:
        return self.agree_with_removal
    
    def _notify_tree_has_not_been_exported(self, name: str) -> None:
        pass

    def _error_if_tree_names_already_taken(self, name: str) -> None:
        pass
    
    def _show_export_info(self, tree_name: str, filepath: str) -> None:
        pass

    def _cannot_load_tree_with_already_taken_name(self, name: str) -> None:
        pass

class Test_Creating_New_Tree(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree',{'name':'New'},children=()))
        self.treelist = treelist.TreeList()
        self.manager = Tree_Manager(self.treelist,tree_tag='Tree')

    def test_creating_new_tree_via_manager(self):
        self.manager.new("Tree 1")
        self.manager.new("Tree 2")
        self.assertListEqual(self.manager.trees, ["Tree 1", "Tree 2"])

    def test_creating_new_tree_with_existing_name(self):
        self.manager.new("Tree X")
        self.manager.new("Tree X")
        self.manager.new("Tree X")
        self.assertListEqual(self.manager.trees, ["Tree X", "Tree X (1)", "Tree X (2)"])

    def test_creating_new_tree_via_ui(self):
        self.manager._buttons[tmg.ButtonID.NEW_TREE].invoke()
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree XY")
        self.manager._buttons[tmg.ButtonID.NEW_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees, ["Tree XY"])
        self.assertFalse(self.manager._window_new.winfo_exists())
        self.assertFalse(self.manager._entry_name.winfo_exists())

    def tearDown(self) -> None:
        treemod.tt.clear()

class Test_Editing_Trees(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree',{'name':'New'},children=()))
        self.treelist = treelist.TreeList()
        self.manager = Tree_Manager(self.treelist,tree_tag='Tree')
        self.manager.new("Tree X")

    def test_rename_tree(self):
        self.assertListEqual(self.manager.trees, ["Tree X"])
        self.manager.rename("Tree X", "Tree Y")
        self.assertListEqual(self.manager.trees, ["Tree Y"])

    def test_renaming_nonexistent_tree_has_no_effect(self):
        self.manager.rename("Nonexistent tree", "Tree Y")
        self.assertListEqual(self.manager.trees, ["Tree X"])

    def test_rename_tree_via_ui(self):
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.assertEqual(self.manager._entry_name.get(),"Tree X")
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertFalse(self.manager._window_rename.winfo_exists())
        self.assertListEqual(self.manager.trees, ["Tree Y"])

    def test_cancelling_the_renaming_in_ui(self):
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.assertEqual(self.manager._entry_name.get(),"Tree X")
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_CANCEL].invoke()
        self.assertFalse(self.manager._window_rename.winfo_exists())
        self.assertListEqual(self.manager.trees, ["Tree X"])

    def test_renaming_tree_to_existing_name_has_no_effect_and_the_rename_window_remains_opened(self):
        self.manager.agree_with_renaming = True
        self.manager.new("Tree Y")
        self.manager._open_right_click_menu(self.manager._view.get_children()[1])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.assertEqual(self.manager._entry_name.get(),"Tree X")

        # renaming to already taken name will not be succesfull and the window stays opened
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertTrue(self.manager._window_rename.winfo_exists())
        self.assertListEqual(self.manager.trees, ["Tree X", "Tree Y"])

        # renaming to some not already take name will take effect and the window closes
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Z")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertFalse(self.manager._window_rename.winfo_exists())
        self.assertListEqual(self.manager.trees, ["Tree Z", "Tree Y"])

    def test_renaming_tree_to_its_original_name_is_allowed(self):
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        # the name is kept unchanged
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertFalse(self.manager._window_rename.winfo_exists())
        self.assertListEqual(self.manager.trees, ["Tree X"])

    def test_renaming_tree_using_right_click(self):
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees,["Tree Y"])

    def test_editing_attributes_of_a_nonexistent_tree_has_no_effect(self):
        self.manager._set_tree_attribute("Nonexistent tree", "some attribute", 123)

    def test_editing_nonexistent_attributes_has_no_effect(self):
        self.assertTrue("Tree X" in self.manager.trees)
        NONEXISTENT_ATTR_NAME = "Attr name"
        self.manager._set_tree_attribute("Tree X", NONEXISTENT_ATTR_NAME,123)
        self.assertTrue(NONEXISTENT_ATTR_NAME not in self.manager.get_tree("Tree X").attributes)

    def tearDown(self) -> None:
        treemod.tt.clear()

class Test_Removing_Trees(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree', {'name':"New"}, children=()))
        self.treelist = treelist.TreeList()
        self.manager = Tree_Manager(self.treelist,tree_tag='Tree')

    def test_remove_tree_using_right_click(self):
        self.manager.agree_with_removal = True
        self.manager.new("Tree X")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_DELETE)
        self.assertListEqual(self.manager.trees, [])

    def test_canceling_the_tree_removal(self):
        self.manager.agree_with_removal = False
        self.manager.new("Tree X")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_DELETE)
        self.assertListEqual(self.manager.trees, ["Tree X"])

    def tearDown(self) -> None:
        treemod.tt.clear()

class Test_Right_Click_Menu(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree', {'name':"New"}, children=()))
        self.treelist = treelist.TreeList()
        self.manager = Tree_Manager(self.treelist, tree_tag='Tree')

    def test_right_click_menu_containts_options_for_creating_or_loading_tree_if_clicked_outside_of_all_items(self):
        self.manager.new("Some tree")
        self.manager._open_right_click_menu("")
        self.assertTrue(self.manager.right_click_menu is not None)
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_NEW)
        self.assertTrue(self.manager._window_new is not None)

    def tearDown(self) -> None:
        treemod.tt.clear()

class Test_Tree_and_Xml_Interaction(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree', {'name':"New", "height":10}, children=()))
        self.treelist = treelist.TreeList()
        self.manager = Tree_Manager(self.treelist,tree_tag='Tree')

    def test_export_and_load_tree(self):
        self.manager.xml_file_path = "./Tree being exported.xml"

        self.manager.new("Tree being exported")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        self.manager.agree_with_removal = True
        self.manager._remove_tree(self.manager.get_tree("Tree being exported"))

        self.assertEqual(self.manager.trees, [])
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()
        self.assertEqual(self.manager.trees, ["Tree being exported"])

    def test_canceling_directory_selection_when_exporting_file(self):
        self.manager.xml_file_path = " " #empty path signifies cancelled file selection
        self.manager.new("Tree to be exported")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        self.assertEqual(self.manager._tree_files, {})

    def test_canceling_file_selection_when_loading_file(self):
        self.manager.xml_file_path = " " #empty path signifies cancelled file selection
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()
        self.assertEqual(self.manager.trees, [])

    def test_loading_from_nonexistent_file_has_no_effect(self):
        self.manager.xml_file_path = "./Nonexistent_file.xml"
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()
        self.assertTrue(self.manager.xml_file_path not in self.manager._tree_files)

    def test_updating_existing_file(self):
        self.manager.xml_file_path = "./Tree being exported.xml"

        self.manager.new("Tree being exported")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        self.manager._set_tree_attribute("Tree being exported","height",15)
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_UPDATE_FILE)

        self.manager.agree_with_removal = True
        self.manager._remove_tree(self.manager.get_tree("Tree being exported"))
        self.assertEqual(self.manager.trees, [])
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()

        self.assertEqual(self.manager.get_tree("Tree being exported").attributes["height"].value, 15)

    def test_removing_the_file_and_then_trying_to_update_it_leads_to_creating_the_file_anew_silently(self):
        self.manager.xml_file_path = "./Tree being exported.xml"

        self.manager.new("Tree being exported")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        exported_file_path = self.manager._tree_files[self.manager.get_tree("Tree being exported")]
        os.remove(exported_file_path)

        self.manager._set_tree_attribute("Tree being exported","height",15)
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_UPDATE_FILE)

        self.manager.agree_with_removal = True
        self.manager._remove_tree(self.manager.get_tree("Tree being exported"))
        self.assertEqual(self.manager.trees, [])
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()

        self.assertEqual(self.manager.get_tree("Tree being exported").attributes["height"].value,15)

    def test_removing_one_tree_and_adding_other_with_the_same_name_cannot_update_the_old_tree_file(self):
        self.manager.xml_file_path = "./Tree being exported.xml"
    
        self.manager.new("Tree being exported")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        self.manager.agree_with_removal = True
        self.manager._remove_tree(self.manager.get_tree("Tree being exported"))
        self.assertListEqual(self.manager.trees,[])
        
        self.manager.agree_with_renaming = True
        # Create new tree and proceed to export it to a file under the same name as the previous one
        self.manager.new("Tree being exported")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])

        self.manager._update_file(self.manager.get_tree("Tree being exported"))
        # The user is prompted to choose a different name 
        self.assertTrue(self.manager._window_rename is not None)

        # After choosing different name, the export might be repeated
        self.manager.xml_file_path = "./Tree being exported 2.xml"
        self.manager._entry_name.insert("end", " 2")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees, ["Tree being exported 2"])
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        self.assertFalse(self.manager._window_rename.winfo_exists())

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("Tree being exported.xml"):
            os.remove("Tree being exported.xml")
        if os.path.isfile("Tree being exported 2.xml"):
            os.remove("Tree being exported 2.xml")
        treemod.tt.clear()

class Test_Exporting_To_Already_Existing_File(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree', {'name':"New"}, children=()))
        self.treelist = treelist.TreeList()
        self.manager = Tree_Manager(self.treelist, tree_tag='Tree')
    
        self.manager.xml_file_path = "./Tree being exported.xml"

        self.manager.new("Tree being exported")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        self.manager.agree_with_removal = True
        self.manager._remove_tree(self.manager.get_tree("Tree being exported"))
        self.assertListEqual(self.manager.trees, [])

        # to the same name as the previously exported and deleted tree
        self.manager.new("Some tree")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree being exported")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertFalse(self.manager._window_rename.winfo_exists())

        # Try to export the new tree with the same name as the old one
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])


    def test_exporting_to_existing_file_name_prompts_the_user_to_rename_the_tree(self):

        # After the user is notified that a file with the tree name already exists in
        # the directory and after he/she clicks OK, the window_rename opens up automatically
        self.manager.agree_with_renaming = True
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        self.assertTrue(self.manager._window_rename.winfo_exists())

    def test_exporting_to_existing_file_and_denying_to_rename_the_tree_aborts_the_export(self):
        # The user chooses to cancel the export
        self.manager.agree_with_renaming = False
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        self.assertFalse(self.manager._window_rename.winfo_exists())

    def tearDown(self) -> None:
        treemod.tt.clear()

class Test_Updating_File_After_Renaming_Tree(unittest.TestCase):

    def test_after_renaming_the_tree_has_to_be_exported_to_a_new_file(self):
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree', {'name':'New'}, children=()))
        tlist = treelist.TreeList()
        manager = Tree_Manager(tlist,tree_tag='Tree')
        manager.xml_file_path = "./Tree being exported.xml"
    
        manager.new("Tree being exported")
        manager._open_right_click_menu(manager._view.get_children()[0])
        manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        manager.rename("Tree being exported", "Tree being exported 2")

        manager._open_right_click_menu(manager._view.get_children()[0])
        # the update option is not available in the right-click menu after
        # renaming the tree
        self.assertRaises(
            tmg.tk.TclError,
            manager.right_click_menu.invoke, 
            tmg.MENU_CMD_TREE_UPDATE_FILE
        )

    def tearDown(self) -> None:  # pragma: no cover
        if os.path.isfile("Tree being exported.xml"):
            os.remove("Tree being exported.xml")
        if os.path.isfile("Tree being exported 2.xml"):
            os.remove("Tree being exported 2.xml")

        treemod.tt.clear()

class Test_Loading_of_Xml(unittest.TestCase):

    def setUp(self) -> None:
        self.tearDown()

        treemod.tt.add(treemod.tt.NewTemplate('Tree', {'name':'New'}, children=()))
        self.manager = Tree_Manager(treelist.TreeList(), tree_tag='Tree')
        self.manager.new("Tree X")
        self.manager.xml_file_path = ("./data/Tree X.xml")
        tree_x = self.manager.get_tree("Tree X")
        # First, export the tree to a xml file and remove it from the manager
        self.manager._export_tree(tree_x)
        self.assertTrue(os.path.isfile("./data/Tree X.xml"))
        self.assertTrue(tree_x in self.manager._tree_files)
        self.manager.agree_with_removal = True
        self.manager._remove_tree(self.manager.get_tree("Tree X"))
        self.assertListEqual(self.manager.trees, [])
        self.assertDictEqual(self.manager._tree_files, {})

    def test_repeated_loading_of_the_same_tree_is_not_allowed(self):
        self.manager._load_tree()
        self.assertListEqual(self.manager.trees, ["Tree X"])
        self.manager._load_tree()
        self.assertListEqual(self.manager.trees, ["Tree X"])

    def tearDown(self) -> None: # pragma: no cover
        if os.path.isfile("./data/Tree X.xml"):
            os.remove("./data/Tree X.xml")
        treemod.tt.clear()


class Test_Actions(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree', {'name':'New'}, children=()))
        tlist = treelist.TreeList()
        self.manager = Tree_Manager(tlist, tree_tag='Tree')
        self.manager.new("Tree X")
        self.manager.new("Tree Y")
    
    def test_action_on_tree_selection(self):
        self.names = []
        def action(tree:treemod.Tree)->None:
            self.names.append(tree.name)
        self.manager.add_action_on_selection(action)
        self.manager._open_right_click_menu(self.manager._view.get_children()[1])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EDIT)
        self.assertListEqual(self.names,["Tree X"])

    def test_action_on_deselection(self):
        self.names = []
        def action(tree:treemod.Tree)->None: self.names.append(tree.name)
        def action2(tree:treemod.Tree)->None: self.names.remove(tree.name)
        self.manager.add_action_on_selection(action)
        self.manager.add_action_on_deselection(action2)
        self.manager._open_right_click_menu(self.manager._view.get_children()[1])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EDIT)
        self.manager._open_right_click_menu(self.manager._view.get_children()[1])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_STOP_EDIT)
        self.assertListEqual(self.names,[])

    def tearDown(self) -> None:
        treemod.tt.clear()


class Test_Specifying_Nonexistent_Tree_Template(unittest.TestCase):

    def test_nonexistent_tree_template_tag_raises_key_error(self)->None:
        treemod.tt.clear()
        treemod.tt.add(treemod.tt.NewTemplate('Tree', {"name":"New"}, children=()))

        tlist = treelist.TreeList('Label')
        self.assertRaises(KeyError, Tree_Manager, tlist, "Nonexistent template tag")


if __name__=="__main__": unittest.main()