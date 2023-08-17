import sys
sys.path.insert(1,"src")


import src.properties as pp
import unittest
from tree import TreeItem, Positive_Int_Attr



class Test_Displaying_Tree_Properties(unittest.TestCase):


    def setUp(self) -> None:
        self.tree = TreeItem(
            "Tree 1", 
            {
                "weight": Positive_Int_Attr(4500), 
                "height": Positive_Int_Attr(12)
            }
        )
        self.prop_window = pp.Properties()
        self.prop_window.display(self.tree)
    
    def test_displayed_properties_agree_with_the_current_attributes(self)->None:
        self.assertEqual(len(self.prop_window.props),3)
        self.assertEqual(self.prop_window.props["name"].cget("text"), f"Tree 1 ({self.tree.tag.lower()})")
        self.assertEqual(self.prop_window.props["weight"].cget("text"), "4500")
        self.assertEqual(self.prop_window.props["height"].cget("text"), "12")

    def test_clear_displayed_properties(self)->None:
        self.prop_window.clear()
        self.assertDictEqual(self.prop_window.props,{})
        self.assertListEqual(self.prop_window.widget.winfo_children(), [])
        # the properties window itself still exists
        self.assertTrue(self.prop_window.widget.winfo_exists())



if __name__=="__main__": unittest.main()




