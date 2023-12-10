from __future__ import annotations
import sys 
sys.path.insert(1,"src")

import unittest
import tkinter as tk
from src.tkgui.editor import Editor_Tk, Lang_Object
from src.core.editor import blank_case_template, new_editor
case_template = blank_case_template()
case_template.configure(currency_code="CZK")
lang = Lang_Object.get_lang_object("./test_hofi_localization/cs_cz.xml")


class Test_Editing_Items_Via_Caseview(unittest.TestCase):

    def setUp(self) -> None:
        amount = case_template.attr.integer(0)
        case_template.add("Item", {"amount":amount, }, child_template_labels=("Item",),)
        case_template.add_case_child_label("Item")
        case_template.add_merging_rule("Item", {"amount":"sum"})
        case_template.set_insertable("Item")

        self.editor = new_editor(case_template, "cs_cz", lang=lang, ignore_duplicit_names=True)
        win = tk.Tk()
        self.editor_ui = Editor_Tk(self.editor, win, ({"amount":("amount",)}), lang = lang,)
        self.editor_ui.configure(precision=2, trailing_zeros=True, use_thousands_separator=True)
        self.case_A = self.editor.new_case("Case A")
        self.parent = self.editor.new(self.case_A, "Item", "Parent")
        self.item_I = self.editor.new(self.parent, "Item", "Item I")
        self.item_II = self.editor.new(self.parent, "Item", "Item II")
        self.item_I.set("amount", 5)
        self.item_II.set("amount", 7)

    def test_merging_items(self)->None:
        self.assertEqual(self.editor_ui.caseview.tree_row_values(self.item_I.id)["amount"], 5)
        self.assertEqual(self.editor_ui.caseview.tree_row_values(self.item_II.id)["amount"], 7)

        merged_item = self.editor.merge({self.item_I, self.item_II})
        self.assertFalse(self.editor_ui.caseview.is_in_view(self.item_I.id))
        self.assertFalse(self.editor_ui.caseview.is_in_view(self.item_II.id))
        self.assertEqual(self.editor_ui.caseview.tree_row_values(merged_item.id)["amount"], 12)
        
        self.editor.undo()
        self.assertTrue(self.editor_ui.caseview.is_in_view(self.item_I.id))
        self.assertTrue(self.editor_ui.caseview.is_in_view(self.item_II.id))
        self.assertEqual(self.editor_ui.caseview.tree_row_values(self.item_I.id)["amount"], 5)
        self.assertEqual(self.editor_ui.caseview.tree_row_values(self.item_II.id)["amount"], 7)

        self.editor.redo()
        self.assertFalse(self.editor_ui.caseview.is_in_view(self.item_I.id))
        self.assertFalse(self.editor_ui.caseview.is_in_view(self.item_II.id))
        self.assertEqual(self.editor_ui.caseview.tree_row_values(merged_item.id)["amount"], 12)

        self.editor.undo()
        self.assertTrue(self.editor_ui.caseview.is_in_view(self.item_I.id))
        self.assertTrue(self.editor_ui.caseview.is_in_view(self.item_II.id))
        self.assertEqual(self.editor_ui.caseview.tree_row_values(self.item_I.id)["amount"], 5)
        self.assertEqual(self.editor_ui.caseview.tree_row_values(self.item_II.id)["amount"], 7)

if __name__=="__main__": 
    unittest.main()
