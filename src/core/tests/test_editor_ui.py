from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.editor import EditorUI, blank_case_template, new_editor


class Test_Editor_UI(unittest.TestCase):

    def setUp(self) -> None:
        self.case_template = blank_case_template()
        attr = self.case_template.attr
        self.case_template.add('Parent', {'weight':attr.quantity('kg', {'k':3}, 0)})
        self.editor = new_editor(self.case_template)
        self.ui = EditorUI(self.editor)
        self.case = self.editor.new_case("New case")

    def test_creating_editor_ui(self)->None:
        self.assertFalse(self.ui.action_menu.is_open)
        self.assertFalse(self.ui.item_window.is_open)
        self.assertFalse(self.ui.planner.is_open)
        self.assertFalse(self.ui.command_running)
        self.assertListEqual(self.ui.selected_items, [])


from src.core.editor import Action_Menu
class Test_Opening_Action_Menu(unittest.TestCase):

    def setUp(self) -> None:
        self.case_template = blank_case_template()
        self.editor = new_editor(self.case_template)
        self.ui = EditorUI(self.editor)
        self.case = self.editor.new_case("New case")

    def test_opening_action_menu_over_tree(self)->None:
        self.ui.open_action_menu(commands={"empty_command":lambda: None}) # pragma: no cover
        self.assertTrue(self.ui.action_menu.is_open)

    def test_opening_action_menu_without_any_commands_raises_exception(self):
        self.assertRaises(Action_Menu.NoCommands, self.ui.open_action_menu, {})

    def test_running_nonexistent_command_raises_exceptino(self):
        self.ui.open_action_menu(commands={"empty_command":lambda: None}) # pragma: no cover
        self.assertRaises(Action_Menu.UndefinedCommand, self.ui.action_menu.run, "undefined command")

    def test_choosing_action_from_menu_runs_the_action_and_closes_the_menu(self)->None:
        self.message = ""
        def cmd_1(): self.message="Run command 1"
        def cmd_2a(): self.message="Run command 2a"
        def cmd_2b(): self.message="Run command 2b"  # pragma: no cover
        commands = {"cmd 1":cmd_1, "cmd 2a":cmd_2a, "cmd 2b":cmd_2b}

        self.ui.open_action_menu(commands = commands)
        self.ui.action_menu.run("cmd 1")
        self.assertEqual(self.message, "Run command 1")
        self.assertFalse(self.ui.action_menu.is_open)

        self.ui.open_action_menu(commands = commands)
        self.ui.action_menu.run("cmd 2a")
        self.assertEqual(self.message, "Run command 2a")


    def test_raising_exception_if_opening_other_ui_parts_while_action_menu_opened(self):
        self.ui.open_action_menu({"empty_command":lambda: None}) # pragma: no cover
        self.assertRaises(EditorUI.ActionMenuOpened, self.ui.open_planner)
        self.assertRaises(EditorUI.ActionMenuOpened, self.ui.open_item_window, self.case)



from src.core.editor import Item_Attribute, Quantity
class Test_Item_Window(unittest.TestCase):

    def setUp(self) -> None:
        self.case_template = blank_case_template()
        attr = self.case_template.attr
        self.case_template.add('Item', {
            'weight':attr.quantity('kg', {'k':3}, 1),
            'description':attr.text('...'),
        })
        self.case_template.add_case_child_label('Item')
        self.editor = new_editor(self.case_template)
        self.ui = EditorUI(self.editor)

        self.case = self.editor.new_case("New case")
        self.item = self.editor.new(self.case, "Item")
        
    def test_opening_and_closing_item_window(self)->None:
        self.ui.open_item_window(self.item)
        self.assertTrue(self.ui.item_window.is_open)
        self.ui.item_window.close()
        self.assertFalse(self.ui.item_window.is_open)

    def test_listing_item_attributes(self)->None:
        self.ui.open_item_window(self.item)
        wattrs = self.ui.item_window.attributes
        self.assertEqual(tuple(wattrs.keys()), ('weight','description'))

        self.assertEqual(wattrs['weight'].orig_value, 1)
        self.assertEqual(wattrs['weight'].options, {'unit':{'kg':('k','g'), 'g':('','g')}})
        self.assertEqual(set(wattrs['weight'].set_funcs.keys()), {'value', 'prefix', 'unit'})
        self.assertEqual(wattrs['description'].orig_value, '...')
        self.assertEqual(wattrs['description'].options, {})
        self.assertDictEqual(wattrs['description'].set_funcs, {
            'value':self.item.attribute('description').set,
        })

    
        


if __name__=="__main__": unittest.main()

