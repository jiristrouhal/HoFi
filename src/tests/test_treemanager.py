import sys
sys.path.insert(1,"src")

import unittest
import treemanager as tmg
import tree as treemod


class Test_Creating_New_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.treemanager = tmg.Tree_Manager()

    def test_creating_new_tree_via_manager(self):
        self.treemanager.new("Tree 1")
        self.assertListEqual(self.treemanager.trees, ["Tree 1"])



if __name__=="__main__": unittest.main()