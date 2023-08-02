import sys 
sys.path.insert(1,"src")

import app
import unittest
import os


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

    def test_renaming_tree(self):
        self.app_instance.new_tree("Tree 1")
        self.app_instance.rename_tree("Tree 1","Tree X")
        self.assertListEqual(self.app_instance.trees,["Tree X"])

    def test_renaming_tree_to_already_taken_name_will_not_take_effect(self):
        self.app_instance.new_tree("Tree 1")
        self.app_instance.new_tree("Tree 2")
        self.app_instance.rename_tree("Tree 2","Tree 1")
        self.assertListEqual(self.app_instance.trees,["Tree 1","Tree 2"])
    
    def test_creating_tree_under_already_existing_name_will_has_no_effect(self):
        self.app_instance.new_tree("Tree 1")
        self.app_instance.new_tree("Tree 1")
        self.assertListEqual(self.app_instance.trees,["Tree 1"])

    def test_removing_nonexistent_tree_does_not_have_effect(self):
        self.app_instance.new_tree("Tree 1")
        self.app_instance.remove_tree("Non-existent tree")
        self.assertListEqual(self.app_instance.trees,["Tree 1"])

    def test_renaming_nonexistent_tree_does_not_have_effect(self):
        self.app_instance.new_tree("Tree 1")
        self.app_instance.rename_tree("Non-existent tree", "Tree X")
        self.assertListEqual(self.app_instance.trees,["Tree 1"])


class Test_Saving_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.app_instance = app.App()

    def test_data_file_path_is_always_set_to_existing_directory(self):
        somepath = app.data_file_path("somefile")
        self.assertTrue(os.path.isdir(os.path.dirname(somepath)))
    
    def test_empty_tree_after_saving_and_loading_is_unchanged(self):
        self.app_instance.new_tree("Tree 1")
        self.app_instance.save_new_tree("Tree 1")
        self.app_instance.remove_tree("Tree 1")
        self.assertListEqual(self.app_instance.trees, [])
        self.app_instance.load_tree("Tree 1")
        self.assertListEqual(self.app_instance.trees, ["Tree 1"])
              

if __name__=="__main__": unittest.main()