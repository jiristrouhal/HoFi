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

    def test_empty_root_element(self):
        tree = app.Tree()
        tree.add_branch(app.Branch(name="Branch 1", weight=50, length=120))
        self.assertListEqual(tree.branches, ["Branch 1"])


if __name__=="__main__": unittest.main()