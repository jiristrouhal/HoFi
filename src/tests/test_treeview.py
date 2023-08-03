import sys 
sys.path.insert(1,"src")


import treeview 
from tree import Tree
import unittest


class Test_Empty_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.view = treeview.Treeview()

    def test_adding_single_tree(self):
        self.view.add_tree(Tree("Tree 1"))
        self.assertEqual(self.view.trees, ("Tree 1",))


if __name__=="__main__": unittest.main()