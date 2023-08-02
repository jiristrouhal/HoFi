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
                             

if __name__=="__main__": unittest.main()