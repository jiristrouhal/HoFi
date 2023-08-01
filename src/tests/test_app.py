import sys 
sys.path.insert(1,"src")

import app
import unittest
import xml.etree.ElementTree as et
import os


class Test_Reading_XML_File(unittest.TestCase):

    def setUp(self) -> None:
        root = et.Element("SomeRootElement")
        et.SubElement(root,"SomeElement")
        et.ElementTree(root).write("./somexml.xml")

    def test_opening_the_existing_data(self):
        tree = app.read_tree_data("./somexml.xml")
        self.assertTrue(tree.getroot() is not None)
        self.assertTrue(tree.getroot().find("SomeElement") is not None)

    def tearDown(self) -> None:
        os.remove("./somexml.xml")


class Test_Creating_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.tree = app.Tree()
        self.tree.add_branch(app.Branch(name="Branch 1", weight=50, length=120))

    def test_add_branch_to_a_tree(self):
        self.assertListEqual(self.tree.branches, ["Branch 1"])

    def test_remove_branch_from_the_tree(self):
        self.tree.add_branch(app.Branch(name="Branch 2", weight=50, length=120))
        removed_branch = self.tree.remove_branch("Branch 2")
        self.assertListEqual(self.tree.branches, ["Branch 1"])
        self.assertTrue(removed_branch is not None)
        self.assertEqual(removed_branch.name, "Branch 2")

    def test_removing_nonexistent_branch_does_not_affect_the_tree(self):
        self.tree.add_branch(app.Branch(name="Branch 2", weight=50, length=120))
        removed_branch = self.tree.remove_branch("Branch 3")
        self.assertListEqual(self.tree.branches, ["Branch 1", "Branch 2"])
        self.assertTrue(removed_branch is None)


if __name__=="__main__": unittest.main()