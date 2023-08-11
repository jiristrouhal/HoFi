import sys
sys.path.insert(1,"src")

import unittest
import treemanager as tmg
import nlist


class Test_Creating_New_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.treelist = nlist.NamedItemsList()
        self.manager = tmg.Tree_Manager(self.treelist)

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
        self.manager._tree_name_entry.delete(0,"end")
        self.manager._tree_name_entry.insert(0,"Tree XY")
        self.manager._buttons[tmg.ButtonID.NEW_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees, ["Tree XY"])
        self.assertEqual(self.manager._new_tree_window, None)
        self.assertEqual(self.manager._tree_name_entry, None)

    def test_rename_tree(self):
        self.manager.new("Tree X")
        self.assertListEqual(self.manager.trees, ["Tree X"])
        self.manager.rename("Tree X", "Tree Y")
        self.assertListEqual(self.manager.trees, ["Tree Y"])

    def test_rename_tree_via_ui(self):
        self.manager.new("Tree X")
        self.manager._view.selection_set(self.manager._view.get_children()[0])
        self.manager._buttons[tmg.ButtonID.RENAME_TREE].invoke()
        self.assertEqual(self.manager._tree_name_entry.get(),"Tree X")
        self.manager._tree_name_entry.delete(0,"end")
        self.manager._tree_name_entry.insert(0,"Tree Y")
        self.manager._buttons[tmg.ButtonID.RENAME_TREE_OK].invoke()
        self.assertEqual(self.manager._rename_tree_window, None)
        self.assertListEqual(self.manager.trees, ["Tree Y"])



if __name__=="__main__": unittest.main()