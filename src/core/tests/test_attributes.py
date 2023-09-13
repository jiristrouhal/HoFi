from __future__ import annotations

import sys 
sys.path.insert(1,"src")


import unittest
from src.core.attributes import new_attribute, Attribute
from src.cmd.commands import Controller


class Test_Accessing_Item_Attributes(unittest.TestCase):

    def setUp(self) -> None:
        self.controller = Controller()
    
    def test_default_attribute_type_is_text(self)->None:
        a1 = new_attribute(self.controller)
        self.assertEqual(a1.type,'text')
        
    def test_setting_other_available_type_of_attribute(self)->None:
        a1 = new_attribute(self.controller,'integer')
        self.assertEqual(a1.type, 'integer')

    def test_setting_attribute_to_invalid_type_raises_error(self)->None:
        self.assertRaises(Attribute.InvalidAttributeType, new_attribute, self.controller, 'invalid_argument_type_0123456789')

    def test_accessing_attribute_value(self)->None:
        a = new_attribute(self.controller,'text')
        a.value
    
    def test_setting_the_attribute_value(self)->None:
        a = new_attribute(self.controller,'text')
        a.set("Some text.")
        self.assertEqual(a.value, "Some text.")

    def test_valid_value(self)->None:
        a = new_attribute(self.controller,'integer')
        self.assertTrue(a.is_valid(5))
        self.assertFalse(a.is_valid("abc"))
        self.assertFalse(a.is_valid("5"))
        self.assertFalse(a.is_valid(""))

    def test_for_text_attribute_any_value_is_valid(self):
        a = new_attribute(self.controller,'text')
        self.assertTrue(a.is_valid(5))
        self.assertTrue(a.is_valid("abc"))
        self.assertTrue(a.is_valid("5"))
        self.assertTrue(a.is_valid(""))

    def test_setting_attribute_to_an_invalid_value_raises_error(self):
        a = new_attribute(self.controller,'integer')
        self.assertRaises(Attribute.InvalidValueType, a.set, "invalid value")


from src.core.attributes import Attribute, Set_Attr_Data
import dataclasses
from src.cmd.commands import Command
from typing import Any


class Test_Undo_And_Redo_Setting_Attribute_Values(unittest.TestCase):

    @dataclasses.dataclass
    class LogBook:
        value:int
    
    @dataclasses.dataclass
    class Write_Data:
        logbook:Test_Undo_And_Redo_Setting_Attribute_Values.LogBook
        attr:Attribute

    @dataclasses.dataclass
    class Write_Value_To_LogBook(Command):
        data:Test_Undo_And_Redo_Setting_Attribute_Values.Write_Data
        prev_value:Any = dataclasses.field(init=False)
        new_value:Any = dataclasses.field(init=False)
        def run(self)->None:
            self.prev_value = self.data.logbook.value
            self.data.logbook.value = self.data.attr.value
            self.new_value = self.data.logbook.value
        def undo(self)->None:
            self.data.logbook.value = self.prev_value
        def redo(self)->None:
            self.data.logbook.value = self.new_value

    def test_undo_and_redo_setting_attribute_values(self):
        controller = Controller()
        logbook = self.LogBook(0)
        volume = Attribute(controller, 'integer', 'volume')
        def  write_to_logbook(data:Set_Attr_Data)->Test_Undo_And_Redo_Setting_Attribute_Values.Write_Value_To_LogBook:
            write_data = self.Write_Data(logbook,data.attr)
            return self.Write_Value_To_LogBook(write_data)
        volume.on_set('test',write_to_logbook,'post')
        volume.set(5)
        volume.set(10)
        self.assertEqual(volume.value,10)

        controller.undo()
        self.assertEqual(volume.value,5)
        controller.redo()
        self.assertEqual(volume.value,10)



class Test_Dependent_Attributes(unittest.TestCase):

    def test_setting_dependency_of_one_attribute_on_another(self):
        controller = Controller()
        DENSITY = 1000
        volume = Attribute(controller, 'integer', "volume")
        mass = Attribute(controller, 'integer', "mass")
        def dependency(volume_attr:Attribute)->int:
            return volume_attr.value*DENSITY
        
        mass.add_dependency(dependency, volume)

        volume.set(2)
        self.assertEqual(mass.value, 2000)

        volume.set(5)
        self.assertEqual(mass.value, 5000)

        controller.undo()
        self.assertEqual(mass.value, 2000)
        controller.redo()
        self.assertEqual(mass.value, 5000)
        controller.undo()
        self.assertEqual(mass.value, 2000)

    def test_chaining_dependency_of_three_attributes(self):
        controller = Controller()
        side = Attribute(controller, 'integer', 'side')
        volume = Attribute(controller, 'integer', 'volume')
        max_n_of_items = Attribute(controller, 'integer', 'max number of items')

        def calc_volume(side:Attribute)->int:
            return side.value**3
        def calc_max_items(volume:Attribute)->int:
            return int(volume.value/0.1)
        
        volume.add_dependency(calc_volume,side)
        max_n_of_items.add_dependency(calc_max_items,volume)

        side.set(1)
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)

        side.set(2)
        self.assertEqual(volume.value,8)
        self.assertEqual(max_n_of_items.value,80)

        controller.undo()
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)
        controller.redo()
        self.assertEqual(volume.value,8)
        self.assertEqual(max_n_of_items.value,80)
        controller.undo()
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)

    def test_calling_set_method_on_dependent_attribute_has_no_effect(self)->None:
        controller = Controller()
        a = Attribute(controller,'integer','a')
        b = Attribute(controller, 'integer', 'b')
        def b_double_of_a(a:Attribute)->int: 
            return 2*a.value
        b.add_dependency(b_double_of_a, a)
        
        a.set(2)
        self.assertEqual(b.value,4)
        b.set(2)
        self.assertEqual(b.value,4)

    def test_removing_dependency(self)->None:
        controller = Controller()
        a = Attribute(controller,'integer','a')
        b = Attribute(controller, 'integer', 'b')
        def b_double_of_a(a:Attribute)->int: 
            return 2*a.value
        b.add_dependency(b_double_of_a, a)

        a.set(2)
        self.assertEqual(b.value,4)

        b.remove_dependencies()
        a.set(1)
        self.assertEqual(b.value,4)

        b.set(5)
        self.assertEqual(b.value,5)

    def test_attribute_cannot_depend_on_itself(self):
        controller = Controller()
        a = Attribute(controller, 'integer', 'a')
        def triple(a:Attribute)->int:  # pragma: no cover
            return 2*a.value
        self.assertRaises(Attribute.CyclicDependency, a.add_dependency, triple, a)

    def test_attribute_indirectly_depending_on_itself_raises_exception(self):
        controller = Controller()
        a = Attribute(controller, 'integer', 'a')
        b = Attribute(controller, 'integer', 'b')
        c = Attribute(controller, 'integer', 'c')
        def equal_to(x:Attribute)->int: # pragma: no cover
            return x.value
        a.add_dependency(equal_to,b)
        b.add_dependency(equal_to,c)
        with self.assertRaises(Attribute.CyclicDependency):
            c.add_dependency(equal_to, a)



if __name__=="__main__": unittest.main()