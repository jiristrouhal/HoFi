import sys 
sys.path.insert(1,"src")

import controls.tree_to_xml as tree_to_xml
import core.tree as treemod
import unittest
import os


class Test_Saving_And_Loading_Trees(unittest.TestCase):

    def setUp(self) -> None:
        treemod.tt.clear()
        treemod.tt.add(
            treemod.tt.NewTemplate('Tree',{'name':"New", "weight":123, "height":20}, children=('Branch',)),
            treemod.tt.NewTemplate('Branch',{'name':"New", "weight":123}, children=('Branch',)),
        )
        self.converter = tree_to_xml.Tree_XML_Converter()
        self.tree1 = treemod.Tree("Tree 1",tag='Tree')

    def test_data_file_path_is_always_set_to_existing_directory(self):
        somepath = tree_to_xml.data_file_path("somefile","data/somedirectory")
        self.assertTrue(os.path.isdir(os.path.dirname(somepath)))
    
    def test_empty_tree_after_saving_and_loading_is_unchanged(self):
        self.converter.save_tree(self.tree1)
        tree = self.converter.load_tree("Tree 1")
        self.assertEqual(tree.name, "Tree 1")

    def test_nonempty_tree_after_saving_and_loading_is_unchanged(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.new("Branch Y",tag='Branch')
        self.converter.save_tree(self.tree1)
        tree = self.converter.load_tree("Tree 1")
        self.assertListEqual(tree.branches(), ["Branch X","Branch Y"])

    def test_nonempty_tree_with_branches_having_child_branches_is_unchanged_after_saving_and_loading_(self):
        sometree = treemod.Tree("SomeTreeX",tag='Tree')
        sometree.set_attribute("weight",100)
        sometree.new("Branch X",tag='Branch')
        sometree.new("Small branch","Branch X",tag='Branch')
        sometree.new("Smaller branch","Branch X","Small branch",tag='Branch')
        
        self.converter.save_tree(sometree)
        loaded_tree = self.converter.load_tree("SomeTreeX")
        self.assertEqual(loaded_tree.attributes["weight"].value, 100)
        self.assertListEqual(loaded_tree.branches(), ["Branch X"])
        self.assertListEqual(loaded_tree.branches("Branch X",), ["Small branch"])
        self.assertListEqual(loaded_tree.branches("Branch X","Small branch"), ["Smaller branch"])

    def test_loading_tree_from_nonexistent_path_returns_none(self):
        self.assertEqual(self.converter.load_tree("Nonexistent tree"), None)
              

if __name__=="__main__": unittest.main()