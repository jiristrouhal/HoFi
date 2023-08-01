import sys 
sys.path.insert(1,"src")

import app
import unittest
import xml.etree.ElementTree as et


class Test_Reading_XML_File(unittest.TestCase):

    def setUp(self) -> None:
        root = et.Element("SomeRootElement")
        et.SubElement(root,"SomeElement")
        et.ElementTree(root).write("./somexml.xml")

    def test_opening_the_existing_data(self):
        tree = app.read_tree("./somexml.xml")
        self.assertTrue(tree.getroot() is not None)
        self.assertTrue(tree.getroot().find("SomeElement") is not None)


if __name__=="__main__": unittest.main()