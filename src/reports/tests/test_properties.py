import sys
sys.path.insert(1,"src")


import unittest
import src.reports.properties as pp
import src.core.tree as tr


class Test_Displaying_Info_Repeatedly(unittest.TestCase):

    def test_no_change_in_properties_if_already_displayed_item_is_claimed_to_be_identical_to_the_current_item(self)->None:
        prop_window = pp.Properties()
        tr.tt.clear()
        tr.tt.add(tr.tt.NewTemplate("Tree", {"name":"NewTree"}, children=()))
        treeA = tr.Tree("TreeA",tag="Tree")
        prop_window.displayed_item = treeA
        self.assertDictEqual(prop_window.props, {})
        prop_window.display(treeA)
        self.assertDictEqual(prop_window.props, {})
        # But if the displayed item is set to some other value (e.g., None), change occurs
        prop_window.displayed_item = None
        prop_window.display(treeA)
        self.assertEqual(prop_window.props["name"].cget("text"),"TreeA (tree)")


if __name__=="__main__": unittest.main()