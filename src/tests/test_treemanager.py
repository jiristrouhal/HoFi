import sys
sys.path.insert(1,"src")

import unittest
import treemanager as tmg


class Test_Creating_New_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.treemanager = tmg.Tree_Manager()

    def test_creating_new_tree_via_manager(self):
        self.treemanager.new("Tree 1")
        self.treemanager.new("Tree 2")
        self.assertListEqual(self.treemanager.trees, ["Tree 1", "Tree 2"])

    def test_creating_new_tree_with_existing_name(self):
        self.treemanager.new("Tree X")
        self.treemanager.new("Tree X")
        self.assertListEqual(self.treemanager.trees, ["Tree X", "Tree X (1)"])

    


if __name__=="__main__": unittest.main()