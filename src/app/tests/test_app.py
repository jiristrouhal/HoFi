import sys 
sys.path.insert(1,'src')

import unittest
import src.app.app as app


class Test_Saving_Tree(unittest.TestCase):

    def test_creating_tree_with_selected_currency(self):

        app.manager._open_new_tree_window()
        app.manager.entries["name"].delete(0,"end")
        app.manager.entries["name"].insert(0,'TreeX')
        app.manager.entries["currency"].delete(0,"end")
        app.manager.entries["currency"].insert(0, 'USD')
        app.manager._confirm_new_tree()

        treeX = app.manager.get_tree('TreeX')
        treeX.new("Income A",tag="Income")
        incomeA = treeX._children[-1]
        self.assertEqual(incomeA.attributes["amount"].currency_code, 'USD')

        

            


if __name__=="__main__": unittest.main()