import sys
sys.path.insert(1,"src")

import unittest
import treemanager as tmg
import nlist
import os


class Test_Creating_New_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.treelist = nlist.NamedItemsList()
        self.manager = tmg.Tree_Manager(self.treelist)
        self.manager._messageboxes_allowed = False

    def test_creating_new_tree_via_manager(self):
        self.manager.new("Tree 1")
        self.manager.new("Tree 2")
        self.assertListEqual(self.manager.trees, ["Tree 1", "Tree 2"])

    def test_creating_new_tree_with_existing_name(self):
        self.manager.new("Tree X")
        self.manager.new("Tree X")
        self.assertListEqual(self.manager.trees, ["Tree X", "Tree X (1)"])

    def test_creating_new_tree_via_ui(self):
        self.manager._buttons[tmg.ButtonID.NEW_TREE].invoke()
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree XY")
        self.manager._buttons[tmg.ButtonID.NEW_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees, ["Tree XY"])
        self.assertEqual(self.manager._window_new, None)
        self.assertEqual(self.manager._entry_name, None)

    def test_rename_tree(self):
        self.manager.new("Tree X")
        self.assertListEqual(self.manager.trees, ["Tree X"])
        self.manager.rename("Tree X", "Tree Y")
        self.assertListEqual(self.manager.trees, ["Tree Y"])

    def test_renaming_nonexistent_tree_has_no_effect(self):
        self.manager.rename("Nonexistent tree", "Tree Y")
        self.assertListEqual(self.manager.trees, [])

    def test_rename_tree_via_ui(self):
        self.manager.new("Tree X")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.assertEqual(self.manager._entry_name.get(),"Tree X")
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertEqual(self.manager._window_rename, None)
        self.assertListEqual(self.manager.trees, ["Tree Y"])

    def test_renaming_tree_to_existing_name_has_no_effect_and_the_rename_window_remains_opened(self):
        self.manager.new("Tree X")
        self.manager.new("Tree Y")
        self.manager._open_right_click_menu(self.manager._view.get_children()[1])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.assertEqual(self.manager._entry_name.get(),"Tree X")

        # renaming to already taken name will not be succesfull and the window stays opened
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertTrue(self.manager._window_rename is not None)
        self.assertListEqual(self.manager.trees, ["Tree X", "Tree Y"])

        # renaming to some not already take name will take effect and the window closes
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Z")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertTrue(self.manager._window_rename is None)
        self.assertListEqual(self.manager.trees, ["Tree Z", "Tree Y"])

    def test_renaming_tree_to_its_original_name_is_allowed(self):
        self.manager.new("Tree X")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        # the name is kept unchanged
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertEqual(self.manager._window_rename, None)
        self.assertListEqual(self.manager.trees, ["Tree X"])

    def test_renaming_tree_using_right_click(self):
        self.manager.new("Tree X")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees,["Tree Y"])

    def test_remove_tree_using_right_click(self):
        self.manager.new("Tree X")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_DELETE)
        self.assertListEqual(self.manager.trees, [])

    def test_right_click_menu_does_not_popup_if_no_item_is_clicked(self):
        self.manager.new("Some tree")
        self.manager._open_right_click_menu("")
        self.assertEqual(self.manager.right_click_menu,None)

    def test_export_and_load_tree(self):
        self.manager.new("Exported tree")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        self.manager._remove_tree(self.manager.get_tree("Exported tree"))
        self.assertEqual(self.manager.trees, [])
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()
        self.assertEqual(self.manager.trees, ["Exported tree"])

    def test_exporting_to_existing_file_name_prompts_the_user_to_rename_the_tree(self):
        self.manager.new("Exported tree")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        self.manager._remove_tree(self.manager.get_tree("Exported tree"))

        # Create new tree with some random name and then rename it 
        # to the same name as the previously exported and deleted tree
        self.manager.new("Some tree")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_RENAME)
        self.manager._entry_name.delete(0,"end")
        self.manager._entry_name.insert(0,"Exported tree")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertTrue(self.manager._window_rename is None)

        # Try to export the new tree with the same name as the old one
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        # After the user is notified that a file with the tree name already exists in
        # the directory and after he/she clicks OK, the window_rename opens up automatically
        self.assertTrue(self.manager._window_rename is not None)

    def test_updating_existing_file(self):
        self.manager.new("Exported tree",attributes={"height":"25"})
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        self.manager._set_tree_attribute("Exported tree","height","15")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_UPDATE_FILE)

        self.manager._remove_tree(self.manager.get_tree("Exported tree"))
        self.assertEqual(self.manager.trees, [])
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()

        self.assertEqual(self.manager.get_tree("Exported tree").attributes["height"], "15")

    def test_removing_the_file_and_then_trying_to_update_it_leads_to_creating_the_file_anew_silently(self):
        self.manager.new("Exported tree",attributes={"height":"25"})
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)

        exported_file_path = self.manager._exported_trees[self.manager.get_tree("Exported tree")]
        os.remove(exported_file_path)

        self.manager._set_tree_attribute("Exported tree","height","15")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_UPDATE_FILE)

        self.manager._remove_tree(self.manager.get_tree("Exported tree"))
        self.assertEqual(self.manager.trees, [])
        self.manager._buttons[tmg.ButtonID.LOAD_TREE].invoke()

        self.assertEqual(self.manager.get_tree("Exported tree").attributes["height"], "15")

    def test_removing_one_tree_and_adding_other_with_the_same_name_cannot_update_the_old_tree_file(self):
        self.manager.new("Exported tree")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        self.manager._remove_tree(self.manager.get_tree("Exported tree"))
        self.assertListEqual(self.manager.trees,[])
        
        # Create new tree and proceed to export it to a file under the same name as the previous one
        self.manager.new("Exported tree")
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager._update_file(self.manager.get_tree("Exported tree"))
        # The user is prompted to choose a different name 
        self.assertTrue(self.manager._window_rename is not None)
        # After choosing different name, the export might be repeated
        self.manager._entry_name.insert("end", " 2")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees, ["Exported tree 2"])
        self.manager._open_right_click_menu(self.manager._view.get_children()[0])
        self.manager.right_click_menu.invoke(tmg.MENU_CMD_TREE_EXPORT)
        self.assertTrue(self.manager._window_rename is None)


    def tearDown(self) -> None:
        if os.path.isfile("Exported tree.xml"):
            os.remove("Exported tree.xml")
        if os.path.isfile("Exported tree 2.xml"):
            os.remove("Exported tree 2.xml")




if __name__=="__main__": unittest.main()