import sys 
sys.path.insert(1,"src")

import app
import unittest


class Test_Managing_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.app_instance = app.App()

    def test_create_new_tree(self):
        self.app_instance.new_tree("Tree 1")
        self.assertListEqual(self.app_instance.trees,["Tree 1"])

    def test_removing_trees(self):
        self.app_instance.new_tree("Tree 1")
        self.app_instance.new_tree("Tree 2")
        self.assertListEqual(self.app_instance.trees,["Tree 1","Tree 2"])
        self.app_instance.remove_tree("Tree 1")
        self.assertListEqual(self.app_instance.trees,["Tree 2"])
        self.app_instance.remove_tree("Tree 2")
        self.assertListEqual(self.app_instance.trees,[])

                             

if __name__=="__main__": unittest.main()