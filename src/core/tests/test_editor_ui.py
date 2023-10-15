from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest


from src.core.editor import new_editor, blank_case_template
from src.core.editor import EditorUI, Item_Menu, Item_Window


class Item_Menu_Test(Item_Menu):
    def _build_menu(self) -> None:
        pass
    def _destroy_menu(self) -> None:
        pass


class Item_Window_Test(Item_Window):
    def _build_window(self,*args) -> None:
        pass
    def _destroy_window(self) -> None:
        pass


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
        self.menu = Item_Menu_Test()
        self.editor_ui = EditorUI(self.editor, self.menu, Item_Window_Test())

    def test_opening_and_closing_action_menu(self):
        self.assertFalse(self.menu.is_open)
        self.editor_ui.open_item_menu(self.editor.root)
        self.assertTrue(self.menu.is_open)   
        self.menu.close()
        self.assertFalse(self.menu.is_open)  

    def test_menu_does_not_open_if_no_actions_are_provided(self):
        self.menu.open({})
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

    def test_opening_item_menu_for_nonexistent_case_raises_exception(self):
        self.assertRaises(
            EditorUI.Opening_Item_Menu_For_Nonexistent_Item, 
            self.editor_ui.open_item_menu, self.editor.root.pick_child("Nonexistent case")
        )

    def test_running_the_command_destroy_the_menu_and_empties_the_actions(self):
        self.menu.open({"command 1":lambda: None})
        self.assertTrue(self.menu.is_open)
        self.assertListEqual(self.menu.action_labels, ["command 1"]) 

        self.menu.run("command 1")
        self.assertFalse(self.menu.is_open)
        self.assertDictEqual(self.menu.actions, {})


class Test_Item_Window(unittest.TestCase):

    def setUp(self) -> None:
        case_template = blank_case_template()
        case_template.add(
            'Parent', 
            {'x':case_template.attr.integer(0)}, 
            child_template_labels=('Child',)
        )
        case_template.add_case_child_label("Parent")
        case_template.add('Child', {'x':case_template.attr.integer(0)},())
        self.editor = new_editor(case_template)
        self.menu = Item_Menu_Test()
        self.item_win = Item_Window_Test()
        self.editor_ui = EditorUI(self.editor, self.menu, self.item_win)
        self.new_case = self.editor.new_case("Case X")
        self.item = self.editor.new(self.new_case, "Parent")

    def test_open_and_close_item_window_for_case(self):
        self.assertFalse(self.item_win.is_open)
        self.editor_ui.open_item_window(self.new_case)
        self.assertTrue(self.item_win.is_open)

    def test_opening_window_for_item_under_new_case(self):
        self.editor_ui.open_item_menu(self.item)
        self.menu.run('edit')
        self.assertTrue(self.item_win.is_open)
        self.item_win.close()
        self.assertFalse(self.item_win.is_open)


if __name__=="__main__": unittest.main()