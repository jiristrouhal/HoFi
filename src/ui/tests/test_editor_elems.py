from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
import tkinter as tk
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
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('choice', init_value='B', options=['A','B','C'])

    def test_entry(self):
        entry = self.cr.new(self.attr, self.master)
        self.assertEqual(entry.value, "B")
        entry.set("A")
        self.assertEqual(entry.value, "A")

    def test_setting_attribute(self)->None:
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, "B")
        entry.set("C")
        self.assertEqual(self.attr.value, "B")
        entry.ok()
        self.assertEqual(self.attr.value, "C")

    def test_revert_changes(self)->None:
        entry = self.cr.new(self.attr, self.master)

        entry.set("A")
        self.assertEqual(entry.value, "A")
        entry.revert()
        self.assertEqual(entry.value, "B")



import datetime
class Test_Date_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('date', init_value=datetime.date(2024,10,25))

    def test_entry(self):
        entry = self.cr.new(self.attr, self.master)
        self.assertEqual(entry.value, datetime.date(2024,10,25))
        entry.set(datetime.date(2025,10,25))
        self.assertEqual(entry.value, datetime.date(2025,10,25))

    def test_setting_attribute(self)->None:
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, datetime.date(2024,10,25))
        entry.set(datetime.date(2000,1,1))
        self.assertEqual(self.attr.value, datetime.date(2024,10,25))
        entry.ok()
        self.assertEqual(self.attr.value, datetime.date(2000,1,1))

    def test_revert_changes(self)->None:
        entry = self.cr.new(self.attr, self.master)

        entry.set(datetime.date(2000,1,1))
        self.assertEqual(entry.value, datetime.date(2000,1,1))
        entry.revert()
        self.assertEqual(entry.value, datetime.date(2024,10,25))

        

class Test_Integer_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('integer', 3)
        self.cr = Entry_Creator()
        self.entry = self.cr.new(self.attr, self.master)

    def test_initial_state_of_integer_entry(self):
        self.assertEqual(self.entry.value, "3")
        self.entry.set("abc")
        self.assertEqual(self.entry.value, "")
        self.entry.set("123")
        self.assertEqual(self.entry.value, "123")

    def test_setting_attribute(self)->None:
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, 3)
        entry.set(-7)
        self.assertEqual(self.attr.value, 3)
        entry.ok()
        self.assertEqual(self.attr.value, -7)

    def test_revert_changes(self)->None:
        entry = self.cr.new(self.attr, self.master)

        entry.set(8)
        self.assertEqual(entry.value, "8")
        entry.revert()
        self.assertEqual(entry.value, "3")


from decimal import Decimal
class Test_Real_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('real', 1.45)

    def test_initial_state_of_real_entry(self):
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(entry.value, "1.45")
        entry.set("abc")
        self.assertEqual(entry.value, "")
        entry.set("12.3")
        self.assertEqual(entry.value, "12.3")

    def test_real_number_entry_with_comma_as_decimal_separator(self):
        fac_cz = attribute_factory(Controller(), 'cs_cz')
        attr_cz = fac_cz.new('real', Decimal('1.45'))
        entry = self.cr.new(attr_cz, self.master)

        self.assertEqual(entry.value, "1,45")
        entry.set("abc")
        self.assertEqual(entry.value, "")
        entry.set("12,3")
        self.assertEqual(entry.value, "12,3")

    def test_setting_attribute(self)->None:
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, Decimal('1.45'))
        entry.set(-5.7)
        self.assertEqual(self.attr.value, Decimal('1.45'))
        entry.ok()
        self.assertEqual(self.attr.value, Decimal('-5.7'))

    def test_revert_changes(self)->None:
        entry = self.cr.new(self.attr, self.master)

        entry.set(8.1)
        self.assertEqual(entry.value, "8.1")
        entry.revert()
        self.assertEqual(entry.value, "1.45")


class Test_Monetary_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('money', 3)

    def test_monetary_entry(self):
        entry = self.cr.new(self.attr, self.master)
        entry.set("abc")
        self.assertEqual(entry.value, "")
        entry.set("12.3")
        self.assertEqual(entry.value, "12.3")
        entry.set("-0.5")
        self.assertEqual(entry.value, "-0.5")

    def test_setting_attribute(self)->None:
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, 3)
        entry.set(-5.7)
        self.assertEqual(self.attr.value, 3)
        entry.ok()
        self.assertEqual(self.attr.value, Decimal('-5.7'))

    def test_revert_changes(self)->None:
        entry = self.cr.new(self.attr, self.master)

        entry.set(8.1)
        self.assertEqual(entry.value, "8.1")
        entry.revert()
        self.assertEqual(entry.value, "3")

    def test_initializing_entry_with_czech_locale_code(self):
        fac_cz = attribute_factory(Controller(), "cs_cz")
        attr = fac_cz.new('money',5.81)
        entry = self.cr.new(attr, self.master)

        self.assertEqual(entry.value,"5,81")


class Test_Text_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('text', "...")

    def test_entry(self):
        entry = self.cr.new(self.attr, self.master)

        entry.set("abc")
        self.assertEqual(entry.value, "abc\n")

    def test_setting_attribute(self)->None:
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, "...")
        entry.set("SomeText")
        self.assertEqual(self.attr.value, "...")
        entry.ok()
        self.assertEqual(self.attr.value, "SomeText")

    def test_revert_changes(self)->None:
        entry = self.cr.new(self.attr, self.master)

        entry.set("SomeText")
        self.assertEqual(entry.value, "SomeText\n")
        entry.revert()
        self.assertEqual(entry.value, "...\n")



class Test_Quantity_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.newqu(0.05, unit="m²", exponents={'c':-4,'m':-6})

    def test_entry(self):
        self.attr.set_prefix('c')
        q = self.cr.new(self.attr, self.master)

        q.set("abc")
        self.assertEqual(q.value, "")

        q.set("25.4")
        self.assertEqual(q.value, "25.4")
        self.assertEqual(q.unit,'cm²')

        q.set_unit('m²')
        self.assertEqual(q.unit,'m²')
        self.assertEqual(q.value, "0.00254")

    def test_setting_attribute(self)->None:
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, Decimal('0.05'))
        entry.set(-5.7)
        self.assertEqual(self.attr.value, Decimal('0.05'))
        entry.ok()
        self.assertEqual(self.attr.value, Decimal('-5.7'))

    def test_revert_changes(self)->None:
        entry = self.cr.new(self.attr, self.master)

        entry.set(8.1)
        self.assertEqual(entry.value, "8.1")
        entry.revert()
        self.assertEqual(entry.value, "0.05")


class Test_Bool_Entry(unittest.TestCase):

    def setUp(self) -> None:
        self.master = tk.Frame()
        self.cr = Entry_Creator()

    def test_entry(self):
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('bool', True)
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(entry.value, True)
        entry.set(False)
        self.assertEqual(entry.value, False)

    def test_setting_attribute(self)->None:
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('bool', True)
        entry = self.cr.new(self.attr, self.master)

        self.assertEqual(self.attr.value, True)
        entry.set(False)
        self.assertEqual(self.attr.value, True)
        entry.ok()
        self.assertEqual(self.attr.value, False)

    def test_revert_changes(self)->None:
        self.fac = attribute_factory(Controller())
        self.attr = self.fac.new('bool', True)
        entry = self.cr.new(self.attr, self.master)

        entry.set(False)
        self.assertEqual(entry.value, False)
        entry.revert()
        self.assertEqual(entry.value, True)



if __name__=="__main__": 
    unittest.main()