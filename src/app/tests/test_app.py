import sys 
sys.path.insert(1,'src')

import unittest
import src.app.app as app


class Test_Saving_Tree(unittest.TestCase):

    pass
    def __test_creating_tree_with_selected_currency(self):

        for currency_code in app.treemod.CURRY_FORMATS.keys():
            app.manager._open_new_tree_window()
            app.manager.entries["name"].delete(0,"end")
            app.manager.entries["name"].insert(0,'TreeX')
            app.manager.entries["currency"].delete(0,"end")
            app.manager.entries["currency"].insert(0, currency_code)
            app.manager._confirm_new_tree()

            treeX = app.manager.get_tree('TreeX')
            treeX.new("Income A",tag="Income")
            incomeA = treeX._children[-1]
            self.assertEqual(incomeA.attributes["amount"].currency_code, currency_code)

        

            


if __name__=="__main__": unittest.main()