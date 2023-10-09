from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from typing import List
import datetime
from src.core.time import Timeline, TimepointInit, Timepoint
from src.core.item import ItemCreator


class Test_Creating_Timeline_And_Timepoints(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(self.root, self.cr._attrfac, timelike_var_label = 'date', timelike_var_type='date')

    def test_defining_timeline_without_any_event_yields_empty_dict_of_timepoints(self):
        self.assertDictEqual(self.tline.points, {})

    def test_passing_item_with_timelike_attribute_does_not_create_any_timepoint_if_timeline_does_not_know_about_the_timelike_attribute(self):
        item = self.cr.new('Item')
        self.root.adopt(item)
        self.assertDictEqual(self.tline.points, {})

    def test_after_specifying_timelike_attribute_label_the_timeline_creates_timepoint_for_every_added_item_with_new_value_of_timelike_attribute(self):
        item_1 = self.cr.new('Item', {'date':'date'})
        item_2 = self.cr.new('Item', {'date':'date'})
        the_date = datetime.date(2021,12,18)
        item_1.set('date', the_date)
        item_2.set('date', the_date)
        self.root.adopt(item_1)
        self.root.adopt(item_2)
        self.assertTrue(the_date in self.tline.points)
        self.cr.undo()
        self.assertTrue(the_date in self.tline.points)
        self.cr.undo()
        self.assertFalse(the_date in self.tline.points)
        self.cr.redo()
        self.cr.redo()
        self.assertTrue(the_date in self.tline.points)

    def test_removing_timepoint_when_leaving_only_item_with_timelike_attribute_corresponding_to_the_timepoint(self):
        item_1 = self.cr.new('Item', {'date':'date'})
        item_2 = self.cr.new('Item', {'date':'date'})
        the_date = datetime.date(2021,12,18)
        item_1.set('date', the_date)
        item_2.set('date', the_date)
        self.root.adopt(item_1)
        self.root.adopt(item_2)

        self.root.leave(item_1)
        self.assertTrue(the_date in self.tline.points)
        self.root.leave(item_2)
        self.assertFalse(the_date in self.tline.points)
        self.cr.undo()
        self.cr.undo()
        self.assertTrue(the_date in self.tline.points)
        self.cr.redo()
        self.cr.redo()
        self.assertFalse(the_date in self.tline.points)

    def test_timepoint_is_not_removed_until_all_items_with_timelike_attribute_corresponding_to_it_are_gone(self):
        item_A = self.cr.new('Item', {'date':'date'})
        item_B = self.cr.new('Item', {'date':'date'})
        the_date = datetime.date(2021,12,18)
        item_A.set('date', the_date)
        item_B.set('date', the_date)
        self.root.adopt(item_A)
        self.root.adopt(item_B)

        self.root.leave(item_A)
        self.assertTrue(the_date in self.tline.points)
        self.root.leave(item_B)
        self.assertFalse(the_date in self.tline.points)


class Test_Init_Timepoint(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(self.root, self.cr._attrfac, 'date', 'date')

    def test_adding_items_to_init_point_raises_exception(self)->None:
        init_point = self.tline.pick_last_point(datetime.date(2023,12,26))
        item = self.cr.new('Item')
        self.assertRaises(TimepointInit.CannotAddItem, init_point._add_item, item)
    
    def test_removing_items_from_init_point_raises_exception(self)->None:
        init_point = self.tline.pick_last_point(datetime.date(2023,12,26))
        item = self.cr.new('Item')
        self.assertRaises(TimepointInit.No_Items_At_Init_Timepoint, init_point._remove_item, item)


from typing import Any
class Test_Finding_Index_Of_Nearest_Smaller_Item_Of_Ordered_List(unittest.TestCase):

    def index_test(self,value:Any, thelist:List[Any], expected_index:int|None)->None:
        self.assertEqual(Timeline._index_of_nearest_smaller(value, thelist), expected_index)

    def test_lists(self)->None:
        self.index_test(4, [], -1)
        self.index_test(4, [5], -1)
        self.index_test(4, [3], 0)
        self.index_test(4, [3,5], 0)
        self.index_test(4, [1,2,6], 1)
        self.index_test(4, [1,2,3], 2)
        self.index_test(4, [1,4,5], 0)
        self.index_test(4, [0,1,4,5,6], 1)
        self.index_test(-10, [0,1,4,5,6], -1)
        self.index_test(1000, [0,1,4,5,6], 4)
        self.index_test(6, [0,1,4,5,6], 3)

class Test_Finding_Index_Of_Nearest_Lesser_Or_Equal_Item_Of_Ordered_List(unittest.TestCase):

    def index_test(self,value:Any, thelist:List[Any], expected_index:int|None)->None:
        self.assertEqual(Timeline._index_of_nearest_smaller_or_equal(value, thelist), expected_index)

    def test_lists(self)->None:
        self.index_test(4, [], -1)
        self.index_test(4, [5], -1)
        self.index_test(4, [3], 0)
        self.index_test(4, [3,5], 0)
        self.index_test(4, [1,2,6], 1)
        self.index_test(4, [1,2,4], 2)
        self.index_test(4, [1,4,5], 1)
        self.index_test(4, [0,1,4,5,6], 2)
        self.index_test(-10, [0,1,4,5,6], -1)
        self.index_test(1000, [0,1,4,5,6], 4)
        self.index_test(6, [0,1,4,5,6], 4)
        self.index_test(4, [4,], 0)



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
        self.tline = Timeline(self.root, self.cr._attrfac, 'seconds', 'integer')

    def test_init_timepoint_is_always_picked_if_no_items_were_added_to_root(self)->None:
        init_point = self.tline.pick_last_point(-6)
        self.assertTrue(init_point.is_init())
        self.assertEqual(self.tline.pick_last_point(10), init_point)
        self.assertEqual(self.tline.pick_last_point(10000), init_point)

    def test_latest_point_before_or_at_given_time_is_picked_if_specified_time_is_at_or_after_first_timepoint(self):
        point1 = self.tline._create_point(3)
        point2 = self.tline._create_point(5)
        self.assertEqual(self.tline.pick_last_point(10), point2)
        self.assertFalse(self.tline.pick_last_point(10).is_init())
        self.assertEqual(self.tline.pick_last_point(5), point2)
        self.assertEqual(self.tline.pick_last_point(4), point1)
        self.assertEqual(self.tline.pick_last_point(3), point1)
        self.assertTrue(self.tline.pick_last_point(2).is_init())


class Test_Timeline_Variable(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(
            self.root, 
            self.cr._attrfac, 
            'date', 
            'date', 
            tvars={'y':self.cr.attr.integer(3), 'z':self.cr.attr.integer(-1)}
        )

    def test_adding_timeline_variable_without_any_timepoints_always_returns_the_initial_value(self):
        self.assertEqual(self.tline('y',datetime.date(1491,4,20)), 3)
        self.assertEqual(self.tline('y',datetime.date(2021,10,18)), 3)
        self.assertEqual(self.tline('y',datetime.date(2081,6,21)), 3)
    
    def test_unbound_timeline_variable_is_unaffected_by_adding_any_timepoints(self):
        item = self.cr.new('Item', {'date':'date', 'x':'integer'})
        item.set('x',5)
        item.set('date',datetime.date(2023,10,15))
        self.root.adopt(item)
        self.assertTrue(len(self.tline.points)==1)
        self.assertEqual(self.tline('y',datetime.date(2023,10,15)), 3)

    def test_binding_timeline_variable(self):
        def add_sum_of_x(y:int, x:List[int])->int:
            return y+sum(x)
        self.tline.bind('y', add_sum_of_x, 'y', '[x:integer]')

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

    def test_setting_initial_value(self):
        self.tline.set_init('y',-5)
        self.assertEqual(self.tline('y',datetime.date(2021,10,18)), -5)
        self.assertRaises(Timeline.UndefinedVariable, self.tline.set_init, 'q', -5)

    def test_setting_mutual_dependencies_of_timeline_variables(self):
        self.tline.bind('z', lambda y: 2*y, 'y')
        self.tline.set_init('y',7)
        self.assertEqual(self.tline('z',datetime.date(2021,10,19)), 14)

    def test_binding_timeline_variables_to_each_other(self):
        def add_sum_of_x(y:int, x:List[int])->int:  # pragma: no cover
            return y+sum(x)
        self.tline.bind('y', add_sum_of_x, 'y', '[x:integer]')
        self.tline.bind('z', lambda z_old, y: 2*y, 'z', 'y')
        itemA = self.cr.new('Item', {'date':'date', 'x':'integer'})
        itemA.set('x',5)
        itemA.set('date',datetime.date(2023,10,15))
        self.root.adopt(itemA)
        self.assertEqual(self.tline('y',datetime.date(2023,10,14)), 3)
        self.assertEqual(self.tline('y',datetime.date(2023,10,15)), 8)
        self.assertEqual(self.tline('z',datetime.date(2023,10,14)), 6)
        self.assertEqual(self.tline('z',datetime.date(2023,10,15)), 16)


    def test_binding_nonexistent_variables_raises_exception(self):
        def add_sum_of_x(y:int, x:List[int])->int:  # pragma: no cover
            return y+sum(x)
        self.assertRaises(
            Timeline.UndefinedVariable,
            self.tline.bind, 'nonexistent_var', add_sum_of_x, 'y', '[x:integer]'
        )

    def test_item_variable_specification_has_to_consist_of_label_and_attribute_type_separated_with_colon_and_enclosed_in_square_brackets(self):
        def add_sum_of_x(y:int, x:List[int])->int: return y+sum(x) # pragma: no cover
        # missing input variable type
        self.assertRaises(
            Timeline.MissingItemVariableType,
            self.tline.bind, 'y', add_sum_of_x, 'y', '[x]'
        )
        # missing input variable label
        self.assertRaises(
            Timeline.MissingItemVariableLabel,
            self.tline.bind, 'y', add_sum_of_x, 'y', '[:integer]'
        )
        # blank input variable type
        self.assertRaises(
            Timeline.MissingItemVariableType,
            self.tline.bind, 'y', add_sum_of_x, 'y', '[x:]'
        )

    def test_using_integer_as_a_timelike_variable(self):
        root = self.cr.new('Root')
        timeline = Timeline(root, self.cr._attrfac, 'seconds', 'integer')
        point1 = timeline._create_point(5)
        point2 = timeline._create_point(8)
        self.assertTrue(timeline.pick_last_point(1).is_init())
        self.assertEqual(timeline.pick_last_point(7), point1)
        self.assertEqual(timeline.pick_last_point(9), point2)
        
        item = self.cr.new('Item', {'seconds':'integer'})
        item.set('seconds', 2)
        root.adopt(item)
        self.assertTrue(2 in timeline.points)

        item_2 = self.cr.new('Item 2', {'seconds':'real'})
        item.set('seconds', 3)
        self.assertRaises(Timeline.TimelikeVariableTypeConflict, root.adopt, item_2)


class Test_Moving_Items_In_Time(unittest.TestCase):

    def test_moving_single_item_removes_its_timepoint_and_creates_new_one(self):
        cr = ItemCreator()
        root = cr.new('Root')
        timeline = Timeline(root, cr._attrfac, 'seconds', 'integer')
        item = cr.new('Item', {'seconds':'integer'})
        item.set('seconds',5)
        root.adopt(item)

        self.assertTrue(5 in timeline.points)

        item.set('seconds',7)
        self.assertFalse(5 in timeline.points)
        self.assertTrue(7 in timeline.points)

        cr.undo()
        self.assertFalse(7 in timeline.points)
        self.assertTrue(5 in timeline.points)

        cr.redo()
        self.assertFalse(5 in timeline.points)
        self.assertTrue(7 in timeline.points)

    def test_moving_one_of_two_items_under_the_same_timepoint_keeps_the_original_timepoint_and_creates_a_new_one(self):
        cr = ItemCreator()
        root = cr.new('Root')
        timeline = Timeline(root, cr._attrfac, 'seconds', 'integer')
        itemA = cr.new('Item A', {'seconds':'integer'})
        itemA.set('seconds',5)
        itemB = cr.new('Item B', {'seconds':'integer'})
        itemB.set('seconds',5)
        root.adopt(itemA)
        root.adopt(itemB)

        self.assertTrue(5 in timeline.points)

        itemA.set('seconds',7)
        self.assertTrue(5 in timeline.points)
        self.assertTrue(7 in timeline.points)

        #after moving the second item also, the original timepoint is deleted
        itemB.set('seconds',7)
        self.assertFalse(5 in timeline.points)
        self.assertTrue(7 in timeline.points)

        cr.undo()
        self.assertTrue(5 in timeline.points)
        self.assertTrue(7 in timeline.points)

        cr.undo()
        self.assertTrue(5 in timeline.points)
        self.assertFalse(7 in timeline.points)

        cr.redo()
        cr.redo()
        self.assertFalse(5 in timeline.points)
        self.assertTrue(7 in timeline.points)

    def test_moving_single_item_while_on_of_timelines_variables_depends_on_items_attribute(self):
        cr = ItemCreator()
        root = cr.new('Root')
        timeline = Timeline(root, cr._attrfac, 'seconds', 'integer', {'y':cr.attr.integer(-5)})
        timeline.bind('y', lambda y0, xlist: y0+sum(xlist), 'y', '[x:integer]')
        item = cr.new('Item', {'seconds':'integer', 'x':'integer'})
        item.set('seconds',15)
        item.set('x',10)
        root.adopt(item)

        self.assertEqual(timeline('y',14), -5)
        self.assertEqual(timeline('y',15), 5)    

        item.set('seconds', 16)
        self.assertEqual(timeline('y',14), -5)
        self.assertEqual(timeline('y',15), -5)    
        self.assertEqual(timeline('y',16), 5)  


class Test_Creating_Timeline_Using_Root_Already_Having_Children(unittest.TestCase):

    def test_adding_root_with_single_chid_creates_necessary_timepoint(self):
        cr = ItemCreator()
        root = cr.new('Root')
        item = cr.new('Item', {'seconds':'integer'})
        item.set('seconds',5)
        root.adopt(item)

        timeline = Timeline(root, cr._attrfac, 'seconds', 'integer')
        self.assertTrue(5 in timeline.points)


class Test_Mutltilevel_Hierarchy(unittest.TestCase):

    def setUp(self) -> None:
        self.cr = ItemCreator()
        self.root = self.cr.new('Root')
        self.tline = Timeline(self.root, self.cr._attrfac, 'seconds', 'integer')
        self.parent = self.cr.new('Parent')
        self.child = self.cr.new('Child', {'seconds':'integer'})
        self.child.set('seconds',7)
        self.grandchild = self.cr.new('Grandchild', {'seconds':'integer'})
        self.grandchild.set('seconds',9)
        self.root.adopt(self.parent)

    def test_item_adopted_by_roots_child_item_is_assigned_a_timepoint(self):
        self.parent.adopt(self.child)
        self.assertTrue(7 in self.tline.points)
        self.child.adopt(self.grandchild)
        self.assertTrue(9 in self.tline.points)

    def test_adopting_item_already_having_a_child(self):
        self.child.adopt(self.grandchild)
        self.parent.adopt(self.child)
        self.assertTrue(7 in self.tline.points)
        self.assertTrue(9 in self.tline.points)

    def test_item_outside_hierarchy_no_longer_interacts_with_the_timeline(self):
        self.root.leave(self.parent)

        # parent now does not affect timepoints
        self.parent.adopt(self.child)
        self.assertFalse(7 in self.tline.points)
        self.child.adopt(self.grandchild)
        self.assertFalse(9 in self.tline.points)

        #after readopting by root, timepoints are readded to the timeline
        self.root.adopt(self.parent)
        self.assertTrue(7 in self.tline.points)
        self.assertTrue(9 in self.tline.points)

        self.cr.undo()
        self.assertFalse(7 in self.tline.points)
        self.assertFalse(9 in self.tline.points)

        self.cr.redo()
        self.assertTrue(7 in self.tline.points)
        self.assertTrue(9 in self.tline.points)

    def test_item_having_child_in_time(self):
        self.parent.adopt(self.child)
        self.child.adopt(self.grandchild)

        self.child.set('seconds', 10)
        self.assertTrue(9 in self.tline.points)
        self.assertTrue(10 in self.tline.points)
        self.assertFalse(7 in self.tline.points)


class Test_Adding_Dependency_After_Adding_An_Item(unittest.TestCase):

    def test_adding_new_dependency_after_adding_an_item(self):
        cr = ItemCreator()
        root = cr.new('Root')
        timeline = Timeline(root, cr._attrfac, 'time', 'integer', {'y':cr.attr.integer(0)})
        itemA = cr.new('Item A', {'time':'integer', 'x':'integer'})
        itemA.multiset({'time':8, 'x':1})

        root.adopt(itemA)
        pointA = timeline.points[8]

        def addsum(y0:int,x:List[int])->int: return y0+sum(x)
        timeline.bind('y', addsum, 'y', '[x:integer]')
        self.assertEqual(len(pointA._item_var_lists['x'].attributes), 1)
        self.assertEqual(timeline('y',7),0)
        self.assertEqual(timeline('y',8),1)


class Test_Switching_Order_Of_Two_Items_In_Time(unittest.TestCase):

    def test_switching_positions_of_two_items_in_time(self):
        cr = ItemCreator()
        root = cr.new('Root')
        timeline = Timeline(root, cr._attrfac, 'time', 'integer', {'y':cr.attr.integer(0)})
        timeline.bind('y', lambda y0,x: y0+sum(x), 'y', '[x:integer]')

        itemA = cr.new('Item A', {'time':'integer', 'x':'integer'})
        itemB = cr.new('Item B', {'time':'integer', 'x':'integer'})
        itemA.multiset({'time':5,'x':1})
        itemB.multiset({'time':8,'x':2})

        root.adopt(itemA)
        root.adopt(itemB)

        self.assertEqual(timeline('y',4), 0)
        self.assertEqual(timeline('y',5), 1)
        self.assertEqual(timeline('y',8), 3)

        itemA.set('time',8)

        self.assertEqual(timeline('y',4), 0)
        self.assertEqual(timeline('y',5), 0)
        self.assertEqual(timeline('y',8), 3)
        self.assertEqual(timeline('y',9), 3)

        itemB.set('time',5)

        self.assertSetEqual(timeline.points[5]._items, {itemB})
        self.assertSetEqual(timeline.points[8]._items, {itemA})
        self.assertEqual(len(timeline.points[5]._item_var_lists['x'].attributes),1)
        self.assertEqual(len(timeline.points[8]._item_var_lists['x'].attributes),1)

        self.assertEqual(timeline('y',4), 0)
        self.assertEqual(timeline('y',5), 2)
        self.assertEqual(timeline('y',8), 3)



if __name__=="__main__":  unittest.main()
