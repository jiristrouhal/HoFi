from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest

from src.core.editor import new_editor, blank_case_template, EditorUI
from src.ui.editor_elems import Item_Menu_Tk


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
        self.menu = Item_Menu_Tk()
        self.editor_ui = EditorUI(self.editor, self.menu)

    def test_opening_and_closing_action_menu(self):
        self.assertFalse(self.menu.is_open)
        self.editor_ui.open_item_menu(self.editor.root)
        self.assertTrue(self.menu.is_open)   
        self.menu.close()
        self.assertFalse(self.menu.is_open)   

    def test_creating_new_case_via_item_menu_opened_for_editor_root_item(self)->None:
        self.editor_ui.open_item_menu(self.editor.root)
        self.assertTrue('new_case' in self.menu.action_labels)
        self.menu.run('new_case')
        self.assertEqual(self.editor.ncases, 1)

    def test_menu_closes_after_running_command(self):
        self.editor_ui.open_item_menu(self.editor.root)
        self.menu.run('new_case')
        self.assertFalse(self.menu.is_open)
 

if __name__=="__main__": 
    unittest.main()