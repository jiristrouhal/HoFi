import sys 
sys.path.insert(1,"src")

import tree_to_xml
import unittest
import os


class Test_Managing_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.converter = tree_to_xml.Tree_XML_Converter()

    def test_create_new_tree(self):
        self.converter.new_tree("Tree 1")
        self.assertListEqual(self.converter.trees,["Tree 1"])

    def test_removing_trees(self):
        self.converter.new_tree("Tree 1")
        self.converter.new_tree("Tree 2")
        self.assertListEqual(self.converter.trees,["Tree 1","Tree 2"])
        self.converter.remove_tree("Tree 1")
        self.assertListEqual(self.converter.trees,["Tree 2"])
        self.converter.remove_tree("Tree 2")
        self.assertListEqual(self.converter.trees,[])

    def test_renaming_tree(self):
        self.converter.new_tree("Tree 1")
        self.converter.rename_tree("Tree 1","Tree X")
        self.assertListEqual(self.converter.trees,["Tree X"])

    def test_renaming_tree_to_already_taken_name_will_not_take_effect(self):
        self.converter.new_tree("Tree 1")
        self.converter.new_tree("Tree 2")
        self.converter.rename_tree("Tree 2","Tree 1")
        self.assertListEqual(self.converter.trees,["Tree 1","Tree 2"])
    
    def test_creating_tree_under_already_existing_name_will_has_no_effect(self):
        self.converter.new_tree("Tree 1")
        self.converter.new_tree("Tree 1")
        self.assertListEqual(self.converter.trees,["Tree 1"])

    def test_removing_nonexistent_tree_does_not_have_effect(self):
        self.converter.new_tree("Tree 1")
        self.converter.remove_tree("Non-existent tree")
        self.assertListEqual(self.converter.trees,["Tree 1"])

    def test_renaming_nonexistent_tree_does_not_have_effect(self):
        self.converter.new_tree("Tree 1")
        self.converter.rename_tree("Non-existent tree", "Tree X")
        self.assertListEqual(self.converter.trees,["Tree 1"])


class Test_Saving_And_Loading_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.converter = tree_to_xml.Tree_XML_Converter()

    def test_data_file_path_is_always_set_to_existing_directory(self):
        somepath = tree_to_xml.data_file_path("somefile")
        self.assertTrue(os.path.isdir(os.path.dirname(somepath)))
    
    def test_empty_tree_after_saving_and_loading_is_unchanged(self):
        self.converter.new_tree("Tree 1")
        self.converter.save_new_tree("Tree 1")
        self.converter.remove_tree("Tree 1")
        self.assertListEqual(self.converter.trees, [])
        self.converter.load_tree("Tree 1")
        self.assertListEqual(self.converter.trees, ["Tree 1"])

    def test_saving_and_loading_nonexistent_tree_takes_no_effect(self):
        self.converter.new_tree("Tree 1")
        self.converter.save_new_tree("Tree x")
        self.converter.load_tree("Tree x")
        self.assertListEqual(self.converter.trees, ["Tree 1"])

    def test_nonempty_tree_after_saving_and_loading_is_unchanged(self):
        self.converter.new_tree("Tree 1")
        self.converter.tree("Tree 1").add_branch("Branch X",attributes={"weight":25})
        self.converter.tree("Tree 1").add_branch("Branch Y",attributes={"weight":30})

        self.converter.save_new_tree("Tree 1")
        self.converter.remove_tree("Tree 1")
        self.converter.load_tree("Tree 1")
        self.assertListEqual(self.converter.tree("Tree 1").branches(), ["Branch X","Branch Y"])

    def test_nonempty_tree_with_branches_having_child_branches_is_unchanged_after_saving_and_loading_(self):
        self.converter.new_tree("Tree 1")
        self.converter.tree("Tree 1").add_branch("Branch X",attributes={"weight":25})
        self.converter.tree("Tree 1").add_branch("Small branch","Branch X",attributes={"weight":10})
        self.converter.tree("Tree 1").add_branch("Smaller branch","Branch X","Small branch",attributes={"weight":5})
        
        self.converter.save_new_tree("Tree 1")
        self.converter.remove_tree("Tree 1")
        self.converter.load_tree("Tree 1")
        self.assertListEqual(self.converter.tree("Tree 1").branches(), ["Branch X"])
        self.assertListEqual(self.converter.tree("Tree 1").branches("Branch X",), ["Small branch"])
        self.assertListEqual(self.converter.tree("Tree 1").branches("Branch X","Small branch"), ["Smaller branch"])
              

if __name__=="__main__": unittest.main()