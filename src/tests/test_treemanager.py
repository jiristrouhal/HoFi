import sys
sys.path.insert(1,"src")

import unittest
import treemanager as tmg


class Test_Creating_New_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.manager = tmg.Tree_Manager()

    def test_creating_new_tree_via_manager(self):
        self.manager.new("Tree 1")
        self.manager.new("Tree 2")
        self.assertListEqual(self.manager.trees, ["Tree 1", "Tree 2"])

    def test_creating_new_tree_with_existing_name(self):
        self.manager.new("Tree X")
        self.manager.new("Tree X")
        self.assertListEqual(self.manager.trees, ["Tree X", "Tree X (1)"])

    def test_creating_new_tree_via_ui(self):
        self.manager.buttons[tmg.ButtonID.NEW_TREE].invoke()
        self.manager.tree_name_entry.delete(0,"end")
        self.manager.tree_name_entry.insert(0,"Tree XY")
        self.manager.buttons[tmg.ButtonID.NEW_TREE_OK].invoke()
        self.assertListEqual(self.manager.trees, ["Tree XY"])

if __name__=="__main__": unittest.main()