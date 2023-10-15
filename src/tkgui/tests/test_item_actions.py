from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
import tkinter as tk

from src.tkgui.item_actions import Item_Window_Tk
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

    def test_setting_attributes_and_confirming_changes_closes_the_window_and_sets_the_attributes_to_new_values(self)->None:
        self.item.multiset({'x':1, 'y':2})
        self.win.open(self.item)
        self.win.entries[0].set(2)
        self.win.entries[1].set(-1)
        self.win.ok()

        self.assertFalse(self.win.is_open)
        self.assertListEqual(self.win.entries, [])

        self.assertEqual(self.item('x'),2)
        self.assertEqual(self.item('y'),-1)
        self.cr.undo()
        self.assertEqual(self.item('x'),1)
        self.assertEqual(self.item('y'),2)


    def test_reverting_changes_done_in_the_item_window(self):
        self.item.multiset({'x':1, 'y':2})
        self.win.open(self.item)
        self.win.entries[0].set(2)
        self.win.entries[1].set(-1)
        self.assertEqual(self.win.entries[0].value, '2')
        self.assertEqual(self.win.entries[1].value, '-1')
        self.win.revert()
        self.assertTrue(self.win.is_open)
        self.assertEqual(self.win.entries[0].value, '1')
        self.assertEqual(self.win.entries[1].value, '2')

    def test_cancelling_changes_done_in_the_item_window_closes_the_window_and_keeps_the_attributes_and_their_original_values(self):
        self.item.multiset({'x':1, 'y':2})
        self.win.open(self.item)
        self.win.entries[0].set(2)
        self.win.entries[1].set(-1)
        self.assertEqual(self.win.entries[0].value, '2')
        self.assertEqual(self.win.entries[1].value, '-1')
        self.win.cancel()
        self.assertFalse(self.win.is_open)
        self.assertListEqual(self.win.entries, [])


if __name__=="__main__": unittest.main()