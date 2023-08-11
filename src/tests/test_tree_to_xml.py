import sys 
sys.path.insert(1,"src")

import tree_to_xml
import tree as treemod
import unittest
import os


class Test_Saving_And_Loading_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.converter = tree_to_xml.Tree_XML_Converter()
        self.tree1 = treemod.Tree("Tree 1")

    def test_data_file_path_is_always_set_to_existing_directory(self):
        somepath = tree_to_xml.data_file_path("somefile","data/somedirectory")
        self.assertTrue(os.path.isdir(os.path.dirname(somepath)))
    
    def test_empty_tree_after_saving_and_loading_is_unchanged(self):
        self.converter.save_tree(self.tree1)
        tree = self.converter.load_tree("Tree 1")
        self.assertEqual(tree.name, "Tree 1")

    def test_nonempty_tree_after_saving_and_loading_is_unchanged(self):
        self.tree1.add_branch("Branch X",attributes={"weight":25})
        self.tree1.add_branch("Branch Y",attributes={"weight":30})
        self.converter.save_tree(self.tree1)
        tree = self.converter.load_tree("Tree 1")
        self.assertListEqual(tree.branches(), ["Branch X","Branch Y"])

    def test_nonempty_tree_with_branches_having_child_branches_is_unchanged_after_saving_and_loading_(self):
        sometree = treemod.Tree("SomeTree")
        sometree.add_branch("Branch X",attributes={"weight":25})
        sometree.add_branch("Small branch","Branch X",attributes={"weight":10})
        sometree.add_branch("Smaller branch","Branch X","Small branch",attributes={"weight":5})
        
        self.converter.save_tree(sometree)
        loaded_tree = self.converter.load_tree("SomeTree")
        self.assertListEqual(loaded_tree.branches(), ["Branch X"])
        self.assertListEqual(loaded_tree.branches("Branch X",), ["Small branch"])
        self.assertListEqual(loaded_tree.branches("Branch X","Small branch"), ["Smaller branch"])
              

if __name__=="__main__": unittest.main()