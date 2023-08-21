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
        pass


if __name__=="__main__": unittest.main()