from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
import tkinter as tk
from src.core.editor import new_editor, EditorUI, blank_case_template
from src.tkgui.item_actions import Item_Window_Tk, Item_Menu_Tk
from src.tkgui.caseview import Case_View_Tk


class Test_View_For_Empty_Editor(unittest.TestCase):

    def setUp(self):
        case_template = blank_case_template()
        self.editor = new_editor(case_template)
        root = tk.Tk()
        menu = Item_Menu_Tk(root)
        item_window = Item_Window_Tk(root)
        self.caseview = Case_View_Tk(root)
        self.ui = EditorUI(self.editor, menu, item_window, self.caseview)

    def test_case_view_initially_contains_no_items(self):
        self.assertTrue(self.caseview.widget.winfo_exists())
        self.assertEqual(self.caseview.widget.get_children(""), ())

    # def test_case_created_in_editor_is_shown_in_treeview(self):
    #     self.editor.new_case("Case A")
    #     self.assertEqual(len(self.caseview.widget.get_children()), 1)



if __name__=="__main__": unittest.main()