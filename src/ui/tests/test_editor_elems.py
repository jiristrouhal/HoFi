from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
import tkinter as tk
from src.ui.editor_elems import Item_Window, Entry_Creator
from src.core.editor import attr_entry_data
from src.core.attributes import attribute_factory
from src.cmd.commands import Controller


class Test_Item_Window(unittest.TestCase):

    def test_starting_item_window(self)->None:
        iwi = Item_Window(None)
        

class Test_Creating_Integer_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('integer', 3)
        self.cr = Entry_Creator()
        entry_data = attr_entry_data(self.attr)
        self.entry = self.cr.new(entry_data, self.master)

    def test_initial_state_of_integer_entry(self):
        self.assertEqual(self.entry.get(), "3")
        self.entry.delete(0,tk.END)    
        self.entry.insert(0, "abc")
        self.assertEqual(self.entry.get(), "")
        self.entry.insert(0, "123")
        self.assertEqual(self.entry.get(), "123")


from decimal import Decimal
class Test_Creating_Real_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_initial_state_of_real_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('real', 3)
        self.entry_data = attr_entry_data(self.attr)
        entry:tk.Entry = self.cr.new(self.entry_data, self.master)

        entry.delete(0,tk.END)    
        entry.insert(0, "abc")
        self.assertEqual(entry.get(), "")
        entry.insert(0, "12.3")
        self.assertEqual(entry.get(), "12.3")

    def test_real_number_entry_with_comma_as_decimal_separator(self):
        self.fac = attribute_factory(Controller(), 'cs_cz')
        self.attr = self.fac.new('real', Decimal('1.45'))
        entry_data = attr_entry_data(self.attr)
        entry:tk.Entry = self.cr.new(entry_data, self.master)

        self.assertEqual(entry.get(), "1,45")
        entry.delete(0,tk.END)    
        entry.insert(0, "abc")
        self.assertEqual(entry.get(), "")
        entry.insert(0, "12,3")
        self.assertEqual(entry.get(), "12,3")

class Test_Monetary_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_monetary_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('money', 3)
        self.entry_data = attr_entry_data(self.attr)
        self.parent_frame:tk.Frame = self.cr.new(self.entry_data, self.master)

        entry = self.parent_frame.nametowidget("entry")

        entry.delete(0,tk.END)    
        entry.insert(0, "abc")
        self.assertEqual(entry.get(), "")
        entry.insert(0, "12.3")
        self.assertEqual(entry.get(), "12.3")
        entry.delete(0,tk.END)  
        entry.insert(0, "-0.5")
        self.assertEqual(entry.get(), "-0.5")

    


if __name__=="__main__": unittest.main()
