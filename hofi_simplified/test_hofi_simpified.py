from __future__ import annotations


import unittest
from hofi_simpified import *


class Test_Setting_File_Path_For_Item_Saving_And_Loading(unittest.TestCase):

    def test_undoing_merge_of_two_items(self):
        new_case = editor.new_case("Case A")
        income_A = editor.new(new_case, "Income", "Income A")
        income_B = editor.new(new_case, "Income", "Income B")
        income_A.set("income_amount", 5)
        income_B.set("income_amount", 8)

        merged = editor.merge(income_A, income_B)
        self.assertEqual(income_A("income_amount"), 5)
        self.assertEqual(income_B("income_amount"), 8)
        self.assertEqual(merged("income_amount"), 13)

        editor.undo()

        self.assertEqual(merged("income_amount"), 0)
        self.assertEqual(income_A("income_amount"), 5)
        self.assertEqual(income_B("income_amount"), 8)


if __name__=="__main__":
    unittest.main()
