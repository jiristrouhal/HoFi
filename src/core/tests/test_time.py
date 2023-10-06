from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.time import create_timeline, blank_timeline_template, Timeline, Timeline_Template
import datetime


class Test_Defining_Timeline(unittest.TestCase):

    def setUp(self) -> None:
        self.tt = blank_timeline_template()
        self.tt.addvar('x',self.tt.attr.integer(5))

    def test_defining_timeline_template(self):
        self.assertRaises(
            Timeline_Template.VariableAlreadyDefined, 
            self.tt.addvar, 'x', self.tt.attr.real(7)
        )

    def test_applying_timeline_template(self):
        tline = create_timeline(self.tt)
        self.assertTrue(tline.has_var('x'))
        self.assertFalse(tline.has_var('y'))
        
    def test_added_variable_retains_its_original_value_if_unaffected_by_any_other_object_or_operation(self):
        tline = create_timeline(self.tt)
        tline.set_init('x',3)
        self.assertEqual(tline('x',datetime.date(2021,11,28)), 3)
        self.assertEqual(tline('x',datetime.date(2022,11,28)), 3)
        self.assertEqual(tline('x',datetime.date(1999,11,28)), 3)

    def test_accessing_nonexistent_variable_raises_exception(self)->None:
        tline = create_timeline(self.tt)
        self.assertRaises(Timeline.UndefinedVariable, tline, 'y', datetime.date(2021,2,23))


class Test_Adding_Item_To_Timeline(unittest.TestCase):

    def setUp(self) -> None:
        self.tt = blank_timeline_template()
        self.tt.addvar('y',self.tt.attr.integer(5))
    
    def test_adding_day_to_timeline(self):
        tline = create_timeline(self.tt)
        tline.add_day(datetime.date(2021,9,15))
        


if __name__=="__main__": unittest.main()

