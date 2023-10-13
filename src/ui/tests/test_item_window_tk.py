from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
import tkinter as tk

from src.ui.editor_elems import Item_Window_Tk
from src.core.item import ItemCreator


class Test_Item_Window(unittest.TestCase):

    def test_opening_and_closing_window(self)->None:
        cr = ItemCreator()
        root = tk.Tk()
        win = Item_Window_Tk(root)
        item = cr.new("Item", {'x':'integer', 'y':'real'})
        win.open(item)
        self.assertTrue(win.is_open)
        self.assertTrue(len(win.entries)==2)

        win.close()
        self.assertFalse(win.is_open)
        self.assertTrue(len(win.entries)==0)


if __name__=="__main__": 
    unittest.main()