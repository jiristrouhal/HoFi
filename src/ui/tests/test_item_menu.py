from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest

from src.core.editor import new_editor, blank_case_template, EditorUI
from src.ui.editor_elems import Item_Menu


class Test_Item_Menu(unittest.TestCase):

    def setUp(self) -> None:
        case_template = blank_case_template()
        case_template.add(
            'Parent', 
            {'x':case_template.attr.integer(0)}, 
            child_template_labels=('Child',)
        )
        case_template.add('Child', {'x':case_template.attr.integer(0)},())
        self.editor = new_editor(case_template)
        menu = Item_Menu(self.editor.root)
        self.editor_ui = EditorUI(self.editor, menu)

    def test_opening_action_menu_on_editor_root(self):
        self.assertFalse(self.editor_ui.item_menu.is_open)
        self.editor_ui.open_item_menu(self.editor.root)
        self.assertTrue(self.editor_ui.item_menu.is_open)



if __name__=="__main__": 
    unittest.main()