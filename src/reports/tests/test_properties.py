import sys
sys.path.insert(1,"src")


import unittest
import src.reports.properties as pp
import src.core.tree as tr
import src.core.tree_templates as temp


class Test_Displaying_Info_Repeatedly(unittest.TestCase):

    def setUp(self) -> None:
        self.prop_window = pp.Properties()
        app_template = temp.AppTemplate('en_us')
        app_template.add(temp.NewTemplate("Tree", {"name":"NewTree"}, children=()))
        self.treeA = tr.Tree("TreeA",tag="Tree",app_template=app_template)

    def test_no_change_in_properties_if_already_displayed_item_is_claimed_to_be_identical_to_the_current_item(self)->None:
        pass


if __name__=="__main__": unittest.main()