import sys
sys.path.insert(1,"src")


import src.properties as pp
import unittest
from tree import TreeItem



class Test_Displaying_Tree_Properties(unittest.TestCase):

    def test_displayed_properties_agree_with_the_current_attributes(self)->None:
        tree = TreeItem("Tree 1", {"weight": 4500, "height": 12})
        prop_window = pp.Properties()
        prop_window.display(tree)
        self.assertEqual(len(prop_window.props),3)
        self.assertEqual(prop_window.props["name"].cget("text"), "Tree 1")
        self.assertEqual(prop_window.props["weight"].cget("text"), "4500")
        self.assertEqual(prop_window.props["height"].cget("text"), "12")


if __name__=="__main__": unittest.main()




