from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
import tkinter as tk

from src.tkgui.item_win import Item_Window_Tk
from src.core.item import ItemCreator


class Test_Item_Window(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = tk.Tk()
        self.win = Item_Window_Tk(self.root)
        self.item = self.cr.new("Item", {'x':'integer', 'y':'real'})

    def test_opening_and_closing_window(self)->None:
        self.win.open(self.item)
        self.assertTrue(self.win.is_open)
        self.assertTrue(len(self.win.entries)==2)

        self.win.close()
        self.assertFalse(self.win.is_open)
        self.assertTrue(len(self.win.entries)==0)

    def test_setting_attributes_and_confirming_changes(self)->None:
        self.item.multiset({'x':1, 'y':2})
        self.win.open(self.item)
        self.win.entries[0].set(2)
        self.win.entries[1].set(-1)
        self.win.ok()
        self.assertEqual(self.item('x'),2)
        self.assertEqual(self.item('y'),-1)
        self.cr.undo()
        self.assertEqual(self.item('x'),1)
        self.assertEqual(self.item('y'),2)
        self.cr.redo()
        self.assertEqual(self.item('x'),2)
        self.assertEqual(self.item('y'),-1)


if __name__=="__main__": unittest.main()