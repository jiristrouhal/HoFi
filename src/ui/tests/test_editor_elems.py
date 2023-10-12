from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
import tkinter as tk
import tkinter.ttk as ttk
from src.ui.editor_elems import Item_Window, Entry_Creator
from src.core.attributes import attribute_factory
from src.cmd.commands import Controller


class Test_Item_Window(unittest.TestCase):

    def test_starting_item_window(self)->None:
        iwi = Item_Window(None)



class Test_Choice_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('choice', init_value='B', options=['A','B','C'])
        entry = self.cr.new(self.attr, self.master)
        self.assertEqual(entry.value(), "B")
        entry.set("A")
        self.assertEqual(entry.value(), "A")



import datetime
class Test_Date_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('date', init_value=datetime.date(2024,10,25))
        entry = self.cr.new(self.attr, self.master)
        self.assertEqual(entry.value(), datetime.date(2024,10,25))
        entry.set(datetime.date(2025,10,25))
        self.assertEqual(entry.value(), datetime.date(2025,10,25))
        

class Test_Integer_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('integer', 3)
        self.cr = Entry_Creator()
        self.entry = self.cr.new(self.attr, self.master)

    def test_initial_state_of_integer_entry(self):
        self.assertEqual(self.entry.value(), "3")
        self.entry.set("abc")
        self.assertEqual(self.entry.value(), "")
        self.entry.set("123")
        self.assertEqual(self.entry.value(), "123")


from decimal import Decimal
class Test_Real_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_initial_state_of_real_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('real', 1.45)
        entry:tk.Entry = self.cr.new(self.attr, self.master)

        self.assertEqual(entry.value(), "1.45")
        entry.set("abc")
        self.assertEqual(entry.value(), "")
        entry.set("12.3")
        self.assertEqual(entry.value(), "12.3")

    def test_real_number_entry_with_comma_as_decimal_separator(self):
        self.fac = attribute_factory(Controller(), 'cs_cz')
        self.attr = self.fac.new('real', Decimal('1.45'))
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(entry.value(), "1,45")
        entry.set("abc")
        self.assertEqual(entry.value(), "")
        entry.set("12,3")
        self.assertEqual(entry.value(), "12,3")

class Test_Monetary_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_monetary_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('money', 3)
        entry = self.cr.new(self.attr, self.master)
        entry.set("abc")
        self.assertEqual(entry.value(), "")
        entry.set("12.3")
        self.assertEqual(entry.value(), "12.3")
        entry.set("-0.5")
        self.assertEqual(entry.value(), "-0.5")


class Test_Text_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('text', "...")
        entry:Attribute_Entry = self.cr.new(self.attr, self.master)

        entry.set("abc")
        self.assertEqual(entry.value(), "abc\n")


class Test_Quantity_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.newqu(0.05, unit="m²", exponents={'c':-4,'m':-6})
        self.attr.set_prefix('c')
        q:Attribute_Entry = self.cr.new(self.attr, self.master)

        q.set("abc")
        self.assertEqual(q.value(), "")

        q.set("25.4")
        self.assertEqual(q.value(), "25.4")
        self.assertEqual(q.value('unit'),'cm²')
        q.set('m²',value_label='unit')
        self.assertEqual(q.value('unit'),'m²')
        self.assertEqual(q.value(), "0.00254")


from src.ui.editor_elems import Attribute_Entry
class Test_Bool_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('bool', True)
        entry:Attribute_Entry = self.cr.new(self.attr, self.master)

        self.assertEqual(entry.value(), True)
        entry.set(False)
        self.assertEqual(entry.value(), False)


        


if __name__=="__main__": unittest.main()
