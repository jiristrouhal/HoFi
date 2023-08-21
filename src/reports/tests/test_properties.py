import sys
sys.path.insert(1,"src")


import unittest
import src.reports.properties as pp
import src.core.tree as tr


class Test_Displaying_Info_Repeatedly(unittest.TestCase):

    def setUp(self) -> None:
        self.prop_window = pp.Properties()
        tr.tt.clear()
        tr.tt.add(tr.tt.NewTemplate("Tree", {"name":"NewTree"}, children=()))
        self.treeA = tr.Tree("TreeA",tag="Tree")

    def test_no_change_in_properties_if_already_displayed_item_is_claimed_to_be_identical_to_the_current_item(self)->None:
        self.prop_window.displayed_item = self.treeA
        self.assertDictEqual(self.prop_window.props, {})
        self.prop_window.display(self.treeA)
        self.assertDictEqual(self.prop_window.props, {})
        # But if the displayed item is set to some other value (e.g., None), change occurs
        self.prop_window.displayed_item = None
        self.prop_window.display(self.treeA)
        self.assertEqual(self.prop_window.props["name"].cget("text"),"TreeA (tree)")

    def test_redrawing_properties(self):
        self.prop_window.display(self.treeA)
        self.assertEqual(self.prop_window.props["name"].cget("text"),"TreeA (tree)")
        self.treeA.rename("TreeB")
        self.prop_window.redraw()
        self.assertEqual(self.prop_window.props["name"].cget("text"),"TreeB (tree)")



if __name__=="__main__": unittest.main()