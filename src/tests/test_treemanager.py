import sys
sys.path.insert(1,"src")

import unittest
import treemanager as tmg
import nlist


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


if __name__=="__main__": unittest.main()