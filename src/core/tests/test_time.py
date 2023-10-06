from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from typing import List
import datetime
from src.core.time import Timeline, Timepoint, TimepointInit
from src.core.item import ItemCreator


class Test_Creating_Timeline_And_Timepoints(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(self.root, self.cr._attrfac, timelike_attr_label = 'date', timelike_attr_type='date')

    def test_defining_timeline_without_any_event_yields_empty_dict_of_timepoints(self):
        self.assertDictEqual(self.tline.timepoints, {})

    def test_passing_item_with_timelike_attribute_does_not_create_any_timepoint_if_timeline_does_not_know_about_the_timelike_attribute(self):
        item = self.cr.new('Item')
        self.root.adopt(item)
        self.assertDictEqual(self.tline.timepoints, {})

    def test_after_specifying_timelike_attribute_label_the_timeline_creates_timepoint_for_every_added_item_with_new_value_of_timelike_attribute(self):
        item = self.cr.new('Item', {'date':'date'})
        the_date = datetime.date(2021,12,18)
        item.set('date', the_date)
        self.root.adopt(item)
        self.assertTrue(the_date in self.tline.timepoints)
        self.cr.undo()
        self.assertFalse(the_date in self.tline.timepoints)
        self.cr.redo()
        self.assertTrue(the_date in self.tline.timepoints)

    def test_removing_timepoint_when_leaving_only_item_with_timelike_attribute_corresponding_to_the_timepoint(self):
        item = self.cr.new('Item', {'date':'date'})
        the_date = datetime.date(2021,12,18)
        item.set('date', the_date)
        self.root.adopt(item)

        self.root.leave(item)
        self.assertFalse(the_date in self.tline.timepoints)
        self.cr.undo()
        self.assertTrue(the_date in self.tline.timepoints)
        self.cr.redo()
        self.assertFalse(the_date in self.tline.timepoints)

    def test_timepoint_is_not_removed_until_all_items_with_timelike_attribute_corresponding_to_it_are_gone(self):
        item_A = self.cr.new('Item', {'date':'date'})
        item_B = self.cr.new('Item', {'date':'date'})
        the_date = datetime.date(2021,12,18)
        item_A.set('date', the_date)
        item_B.set('date', the_date)
        self.root.adopt(item_A)
        self.root.adopt(item_B)

        self.root.leave(item_A)
        self.assertTrue(the_date in self.tline.timepoints)
        self.root.leave(item_B)
        self.assertFalse(the_date in self.tline.timepoints)


class Test_Init_Timepoint(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(self.root, self.cr._attrfac, 'date', 'date')

    def test_adding_items_to_init_point_raises_exception(self)->None:
        init_point = self.tline.pick_point(datetime.date(2023,12,26))
        item = self.cr.new('Item')
        self.assertRaises(TimepointInit.CannotAddItem, init_point._add_item, item)
    
    def test_removing_items_from_init_point_raises_exception(self)->None:
        init_point = self.tline.pick_point(datetime.date(2023,12,26))
        item = self.cr.new('Item')
        self.assertRaises(TimepointInit.No_Items_At_Init_Timepoint, init_point._remove_item, item)


class Test_Insert_Into_Ordered_List(unittest.TestCase):

    def test_insert_into_empty_list(self)->None:
        thelist:List[float] = []
        Timeline.insert(5,thelist)
        self.assertListEqual(thelist, [5])

    def test_insert_value_larger_than_list_max(self)->None:
        thelist:List[float] = [7,8]
        Timeline.insert(10,thelist)
        self.assertListEqual(thelist, [7,8,10])

    def test_insert_value_smaller_than_list_min(self)->None:
        thelist:List[float] = [7,8]
        Timeline.insert(5,thelist)
        self.assertListEqual(thelist, [5,7,8])

    def test_inserting_already_present_value_has_no_effect(self)->None:
        thelist:List[float] = [7,8]
        Timeline.insert(7,thelist)
        self.assertListEqual(thelist, [7,8])

    def test_inserting_value_between_two_list_values(self)->None:
        thelist:List[float] = [7,8]
        Timeline.insert(7.9, thelist)
        self.assertListEqual(thelist, [7, 7.9, 8])


class Test_Picking_Timepoints(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(self.root, self.cr._attrfac, 'date', 'date')

    def test_init_timepoint_is_always_picked_if_no_items_were_added_to_root(self)->None:
        init_point = self.tline.pick_point(datetime.date(2023,12,26))
        self.assertTrue(init_point.is_init())
        self.assertEqual(self.tline.pick_point(datetime.date(2123,12,26)), init_point)
        self.assertEqual(self.tline.pick_point(datetime.date(1823,12,26)), init_point)

    def test_latest_point_before_or_at_given_time_is_picked_if_specified_time_is_at_or_after_first_timepoint(self):
        point1 = self.tline.create_timepoint(datetime.date(1900,3,20),self.tline)
        point2 = self.tline.create_timepoint(datetime.date(2000,3,20),self.tline)
        self.tline._add_timepoint(point1)
        self.tline._add_timepoint(point2)
        self.assertEqual(self.tline.pick_point(datetime.date(2100,3,20)), point2)
        self.assertEqual(self.tline.pick_point(datetime.date(2000,3,20)), point2)
        self.assertEqual(self.tline.pick_point(datetime.date(1950,3,20)), point1)
        self.assertEqual(self.tline.pick_point(datetime.date(1900,3,20)), point1)
        self.assertTrue(self.tline.pick_point(datetime.date(1800,3,20)).is_init())


class Test_Timeline_Variable(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(self.root, self.cr._attrfac, 'date', 'date', tvars={'y':self.cr.attr.integer(3)})

    def test_adding_timeline_variable_without_any_timepoints_always_returns_the_initial_value(self):
        self.assertEqual(self.tline('y',datetime.date(1491,4,20)), 3)
        self.assertEqual(self.tline('y',datetime.date(2021,10,18)), 3)
        self.assertEqual(self.tline('y',datetime.date(2081,6,21)), 3)
    
    def test_unbound_timeline_variable_is_unaffected_by_adding_any_timepoints(self):
        item = self.cr.new('Item', {'date':'date', 'x':'integer'})
        item.set('x',5)
        item.set('date',datetime.date(2023,10,15))
        self.root.adopt(item)
        self.assertTrue(len(self.tline.timepoints)==1)
        self.assertEqual(self.tline('y',datetime.date(2023,10,15)), 3)

    def test_binding_timeline_variable(self):
        def add_sum_of_x(y:int, x:List[int])->int:
            return y+sum(x)
        self.tline.bind('y', add_sum_of_x, '[x:integer]')

        itemA = self.cr.new('Item', {'date':'date', 'x':'integer'})
        itemB = self.cr.new('Item', {'date':'date', 'x':'integer'})
        itemA.set('x',5)
        itemB.set('x',2)
        itemA.set('date',datetime.date(2023,10,15))
        itemB.set('date',datetime.date(2023,10,17))
        self.root.adopt(itemA)
        self.root.adopt(itemB)

        self.assertEqual(self.tline('y',datetime.date(2023,10,14)), 3)
        self.assertEqual(self.tline('y',datetime.date(2023,10,15)), 8)
        self.assertEqual(self.tline('y',datetime.date(2023,10,16)), 8)
        self.assertEqual(self.tline('y',datetime.date(2023,10,17)), 10)
        self.assertEqual(self.tline('y',datetime.date(2023,11,17)), 10)
        
        self.cr.undo()
        self.assertEqual(self.tline('y',datetime.date(2023,11,17)), 8)

    def test_binding_nonexistent_variables_raises_exception(self):
        def add_sum_of_x(y:int, x:List[int])->int:
            return y+sum(x)
        self.assertRaises(
            Timeline.BindingNonexistentVarible,
            self.tline.bind, 'nonexistent_var', add_sum_of_x, '[x:integer]'
        )

    def test_using_integer_as_a_timelike_variable(self):
        timeline = Timeline(self.root, self.cr._attrfac, 'seconds', 'integer')
        point1 = timeline.create_timepoint(5)
        point2 = timeline.create_timepoint(8)
        timeline._add_timepoint(point1)
        timeline._add_timepoint(point2)
        self.assertTrue(timeline.pick_point(1).is_init())
        self.assertEqual(timeline.pick_point(7), point1)
        self.assertEqual(timeline.pick_point(9), point2)

    


if __name__=="__main__": unittest.main()

