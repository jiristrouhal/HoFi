from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.editor import EditorUI


class Test_Editor_UI(unittest.TestCase):

    def test_creating_editor_ui(self)->None:
        ui = EditorUI()
        self.assertFalse(ui.action_menu.is_open)
        self.assertFalse(ui.item_window.is_open)
        self.assertFalse(ui.command_running)
        self.assertListEqual(ui.selected_items, [])

    


if __name__=="__main__": unittest.main()

