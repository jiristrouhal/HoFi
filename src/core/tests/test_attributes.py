from __future__ import annotations

import sys 
sys.path.insert(1,"src")


import unittest
import dataclasses
from typing import Any

from src.core.attributes import attribute_factory, Attribute, Set_Attr_Data
from src.cmd.commands import Controller, Command


class Test_Accessing_Item_Attributes(unittest.TestCase):

    def setUp(self) -> None:
        self.attrfac = attribute_factory(Controller())
    
    def test_default_attribute_type_is_text(self)->None:
        a1 = self.attrfac.new()
        self.assertEqual(a1.type,'text')
        
    def test_setting_other_available_type_of_attribute(self)->None:
        a1 = self.attrfac.new('integer')
        self.assertEqual(a1.type, 'integer')

    def test_setting_attribute_to_invalid_type_raises_error(self)->None:
        self.assertRaises(Attribute.InvalidAttributeType, self.attrfac.new, 'invalid_argument_type_0123456789')

    def test_accessing_attribute_value(self)->None:
        a = self.attrfac.new('text')
        a.value
    
    def test_setting_the_attribute_value(self)->None:
        a = self.attrfac.new('text')
        a.set("Some text.")
        self.assertEqual(a.value, "Some text.")

    def test_valid_value(self)->None:
        a = self.attrfac.new('integer')
        self.assertTrue(a.is_valid(5))
        self.assertFalse(a.is_valid(0.5))
        self.assertFalse(a.is_valid("abc"))
        self.assertFalse(a.is_valid("5"))
        self.assertFalse(a.is_valid(""))

    def test_for_text_attribute_any_string_value_is_valid(self):
        a = self.attrfac.new('text')
        self.assertFalse(a.is_valid(5))
        self.assertTrue(a.is_valid("abc"))
        self.assertTrue(a.is_valid("5"))
        self.assertTrue(a.is_valid(""))
        self.assertTrue(a.is_valid("   "))

    def test_setting_attribute_to_an_invalid_value_raises_error(self):
        a = self.attrfac.new('integer')
        self.assertRaises(Attribute.InvalidValueType, a.set, "invalid value")

    def test_real_attribute_valid_inputs(self):
        x = self.attrfac.new('real')
        self.assertTrue(x.is_valid(0))
        self.assertTrue(x.is_valid(1))
        self.assertTrue(x.is_valid(-1))
        self.assertTrue(x.is_valid(0.5))
        self.assertTrue(x.is_valid(1/5))
        self.assertTrue(x.is_valid(math.e))
        self.assertTrue(x.is_valid(math.nan))
        self.assertTrue(x.is_valid(math.inf))

        self.assertFalse(x.is_valid(None))
        self.assertFalse(x.is_valid(""))
        self.assertFalse(x.is_valid(" "))
        self.assertFalse(x.is_valid("5"))
        self.assertFalse(x.is_valid("0.5"))
        self.assertFalse(x.is_valid("a"))
        self.assertFalse(x.is_valid(complex(1,2)))
        self.assertFalse(x.is_valid(complex(1,0)))



from src.core.attributes import Attribute_Factory
class Test_Defining_Custom_Attribute_Type(unittest.TestCase):

    class Positive_Integer_Attribute(Attribute):
        default_value = 1
        def is_valid(self, value: Any) -> bool:
            try:
                x = int(value)
                return x is value and x>0
            except: 
                return False
            
        def read(self,text:str)->None: # pragma: no cover
            pass
            
        @classmethod
        def _str_value(cls, value, **options) -> str: # pragma: no cover
            return str(value)
            
    def test_defining_positive_integer_attribute(self):
        attrfac = attribute_factory(Controller())
        attrfac.add('positive integer', self.Positive_Integer_Attribute)
        attr = attrfac.new('positive integer')
        attr.set(5)
        self.assertEqual(attr.value, 5)
        self.assertFalse(attr.is_valid("abc"))
        self.assertFalse(attr.is_valid(0))
        self.assertFalse(attr.is_valid(-1))
        self.assertFalse(attr.is_valid(0.5))
        self.assertRaises(Attribute.InvalidValueType, attr.set, 0)
        self.assertRaises(Attribute.InvalidValueType, attr.set, -1)
        self.assertRaises(Attribute.InvalidValueType, attr.set, 0.5)

    def test_adding_new_attribute_type_under_already_taken_label_raises_exception(self):
        attrfac = attribute_factory(Controller())
        with self.assertRaises(Attribute_Factory.TypeAlreadyDefined):
            attrfac.add('integer', self.Positive_Integer_Attribute)


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
        fac = attribute_factory(Controller())
        logbook = self.LogBook(0)
        volume = fac.new('integer', 'volume')
        def  write_to_logbook(data:Set_Attr_Data)->Test_Undo_And_Redo_Setting_Attribute_Values.Write_Value_To_LogBook:
            write_data = self.Write_Data(logbook,data.attr)
            return self.Write_Value_To_LogBook(write_data)
        volume.on_set('test',write_to_logbook,'post')
        volume.set(5)
        volume.set(10)
        self.assertEqual(volume.value,10)

        fac.controller.undo()
        self.assertEqual(volume.value,5)
        fac.controller.redo()
        self.assertEqual(volume.value,10)


class Test_Dependent_Attributes(unittest.TestCase):
    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())

    def test_dependent_attribute_must_depend_at_least_on_one_attribute(self):
        x = self.fac.new("integer")
        y = self.fac.new("integer")
        def invalid_dependency(): return 5 # pragma: no cover
        self.assertRaises(Attribute.NoInputsForDependency, y.add_dependency, invalid_dependency)

    def test_setting_dependency_of_one_attribute_on_another(self):
        DENSITY = 1000
        volume = self.fac.new('integer', "volume")
        mass = self.fac.new('integer', "mass")
        def dependency(volume:int)->int:
            return volume*DENSITY
        
        mass.add_dependency(dependency, volume)

        volume.set(2)
        self.assertEqual(mass.value, 2000)

        volume.set(5)
        self.assertEqual(mass.value, 5000)

        self.fac.controller.undo()
        self.assertEqual(mass.value, 2000)
        self.fac.controller.redo()
        self.assertEqual(mass.value, 5000)
        self.fac.controller.undo()
        self.assertEqual(mass.value, 2000)

    def test_chaining_dependency_of_three_attributes(self):
        side = self.fac.new('integer', 'side')
        volume = self.fac.new('integer', 'volume')
        max_n_of_items = self.fac.new('integer', 'max number of items')

        def calc_volume(side:int)->int:
            return side**3
        def calc_max_items(volume:int)->int:
            return int(volume/0.1)
        
        volume.add_dependency(calc_volume,side)
        max_n_of_items.add_dependency(calc_max_items,volume)

        side.set(1)
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)

        side.set(2)
        self.assertEqual(volume.value,8)
        self.assertEqual(max_n_of_items.value,80)

        self.fac.controller.undo()
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)
        self.fac.controller.redo()
        self.assertEqual(volume.value,8)
        self.assertEqual(max_n_of_items.value,80)
        self.fac.controller.undo()
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)

    def test_adding_second_dependency_raises_exception(self):
        x = self.fac.new('integer','x')
        y = self.fac.new('integer','y')
        def x_squared(x:int)->int: return x*x # pragma: no cover
        y.add_dependency(x_squared,x)
        self.assertRaises(Attribute.DependencyAlreadyAssigned, y.add_dependency, x_squared,x)
        # after breaking dependency, it is possible to reassign new dependency
        y.break_dependency()
        y.add_dependency(x_squared,x)
        self.assertRaises(Attribute.DependencyAlreadyAssigned, y.add_dependency, x_squared,x)

    def test_calling_set_method_on_dependent_attribute_has_no_effect(self)->None:
        a = self.fac.new('integer','a')
        b = self.fac.new('integer', 'b')
        def b_double_of_a(a:int)->int: 
            return 2*a
        b.add_dependency(b_double_of_a, a)
        
        a.set(2)
        self.assertEqual(b.value,4)
        b.set(2)
        self.assertEqual(b.value,4)

    def test_removing_dependency(self)->None:
        a = self.fac.new('integer','a')
        b = self.fac.new('integer', 'b')
        def b_double_of_a(a:int)->int: 
            return 2*a
        b.add_dependency(b_double_of_a, a)

        a.set(2)
        self.assertEqual(b.value,4)

        b.break_dependency()
        a.set(1)
        self.assertEqual(b.value,4)

        b.set(5)
        self.assertEqual(b.value,5)

    def test_attribute_cannot_depend_on_itself(self):
        a = self.fac.new('integer', 'a')
        def triple(a:int)->int:  # pragma: no cover
            return 2*a
        self.assertRaises(Attribute.CyclicDependency, a.add_dependency, triple, a)

    def test_attribute_indirectly_depending_on_itself_raises_exception(self):
        a = self.fac.new('integer', 'a')
        b = self.fac.new('integer', 'b')
        c = self.fac.new('integer', 'c')
        def equal_to(x:int)->int: # pragma: no cover
            return x
        a.add_dependency(equal_to,b)
        b.add_dependency(equal_to,c)
        with self.assertRaises(Attribute.CyclicDependency):
            c.add_dependency(equal_to, a)

    def test_dependent_attribute_is_updated_immediatelly_after_adding_the_dependency(self):
        x = self.fac.new('integer','x')
        x.set(2)
        y = self.fac.new('integer','y')
        y.set(0)
        def double(x:int)->int: return 2*x

        self.assertEqual(y.value,0)
        y.add_dependency(double,x)
        self.assertEqual(y.value,4)


class Test_Correspondence_Between_Dependency_And_Attributes(unittest.TestCase):

    def test_assigning_invalid_attribute_type_for_dependency_function_argument_raises_exception(self):
        fac = Attribute_Factory(Controller())
        x = fac.new('text',"x")
        y = fac.new('integer',"y")
        def y_of_x(x:int)->int: return x*x # pragma: no cover
        with self.assertRaises(Attribute.WrongAttributeTypeForDependencyInput):
            y.add_dependency(y_of_x,x)

    def test_adding_dependency_with_return_type_not_matching_the_dependent_attribute_raises_exception(self):
        fac = Attribute_Factory(Controller())
        x = fac.new('integer',"x")
        y = fac.new('text',"y")
        def y_of_x(x:int)->int: return x*x # pragma: no cover
        with self.assertRaises(Attribute.WrongAttributeTypeForDependencyOutput):
            y.add_dependency(y_of_x,x)


from src.core.attributes import Dependency
from math import inf
import math
class Test_Dependency_Object(unittest.TestCase):

    def test_dependency_with_function_taking_any_real_number(self):
        def square(x:int)->int: return x*x
        dep = Dependency(square)
        self.assertEqual(dep(2),4)
        self.assertEqual(dep(0),0)
        self.assertEqual(dep(inf), inf)
        self.assertEqual(dep(0),0)

    def test_dependency_with_function_taking_positive_real_numbers(self):
        def square_root(x:int)->float: return math.sqrt(x)
        dep = Dependency(square_root)
        self.assertEqual(dep(4),2)
        self.assertEqual(dep(0),0)
        self.assertEqual(dep(inf), inf)
        self.assertTrue(math.isnan(dep(-1)))

    def test_passing_invalid_argument_type_to_dependency(self):
        def square(x:int)->int: return x*x
        dep = Dependency(square)
        self.assertRaises(Dependency.InvalidArgumentType, dep, "abc")



class Test_Using_Dependency_Object_To_Handle_Invalid_Input_Values(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = Attribute_Factory(Controller())
    
    def test_raise_exception_when_using_attribute_with_incorrect_type(self):
        x = self.fac.new('text',"x")
        y = self.fac.new('integer',"y")
        def y_of_x(x:int)->int: return x*x # pragma: no cover
        with self.assertRaises(Attribute.WrongAttributeTypeForDependencyInput):
            y.add_dependency(Dependency(y_of_x),x)

    def test_handle_input_outside_of_the_function_domain_in_dependent_attribute_calculation(self):
        x = self.fac.new('integer',"x")
        y = self.fac.new('real',"y")
        def y_of_x(x:int)->float: return math.sqrt(x) # pragma: no cover
        y.add_dependency(Dependency(y_of_x),x)
        x.set(-1)
        self.assertTrue(math.isnan(y.value))

    def test_handle_input_outside_of_the_function_when_adding_the_dependency(self):
        x = self.fac.new('integer',"x")
        x.set(-1)
        y = self.fac.new('real',"y")

        def y_of_x(x:int)->float: return math.sqrt(x) # pragma: no cover
        y.add_dependency(Dependency(y_of_x),x)
        self.assertTrue(math.isnan(y.value))

    def test_division_by_zero(self)->None:
        x = self.fac.new('real',"x")
        x.set(0)
        y = self.fac.new('real',"y")

        def y_of_x(x:float)->float: return 1/x 
        y.add_dependency(Dependency(y_of_x),x)
        self.assertTrue(math.isnan(y.value))


class Test_Copying_Attribute(unittest.TestCase):

    def setUp(self)->None:
        self.fac = attribute_factory(Controller())

    def test_copy_independent_attribute(self)->None:
        x = self.fac.new("integer", 'x')
        x.set(5)

        self.assertEqual(x.value, 5)
        x_copy = x.copy()
        self.assertEqual(x_copy.value, 5)
        self.assertEqual(x_copy.type, 'integer')
        self.assertTrue(x_copy._id != x._id)
    
    def test_copying_the_attribute_also_copies_its_dependencies(self)->None:
        x = self.fac.new("integer", 'x')
        x.set(2)
        y = self.fac.new("integer", 'y')
        def double(x:int)->int: return 2*x

        y.add_dependency(Dependency(double),x)

        self.assertSetEqual(y._depends_on,{x})
        y_copy = y.copy()
        self.assertSetEqual(y_copy._depends_on,{x}) 

        # test that both y are affected by change in x value
        x.set(2)
        self.assertEqual(y.value,4)
        self.assertEqual(y_copy.value,4)
        #test breaking the original y dependency
        y.break_dependency()
        x.set(3)
        self.assertEqual(y.value,4)
        self.assertEqual(y_copy.value,6)


    @dataclasses.dataclass
    class Message:
        text:str = ""
    
    @dataclasses.dataclass
    class Write_Value_To_Message_Text:
        attr:Attribute
        message:Test_Copying_Attribute.Message
        prev_text:str = dataclasses.field(init=False)
        new_text:str = dataclasses.field(init=False)
        def run(self):
            self.prev_text = self.message.text
            self.message.text = str(self.attr.value)
            self.new_text = self.message.text
        def undo(self): # pragma: no cover
            self.message.text = self.prev_text
        def redo(self): # pragma: no cover
            self.message.text = self.new_text

    def test_copying_the_attribute_does_not_copy_those_commands_added_after_the_original_attribute_initialization(self):
        x = self.fac.new("integer", 'x')
        x.set(2)
        message = self.Message()
        def write_value_to_message_txt(data:Set_Attr_Data)->Test_Copying_Attribute.Write_Value_To_Message_Text:
            return self.Write_Value_To_Message_Text(x,message)
        x.command['set'].add('test',write_value_to_message_txt,'post')

        x_copy = x.copy()
        x.set(5)
        self.assertEqual(message.text,"5")
        x_copy.set(511651654547)
        self.assertEqual(message.text,"5")

    def test_attribute_basic_commands_are_not_identical_to_those_of_its_copy(self):
        x = self.fac.new("integer", 'x')
        x_copy = x.copy()
        for label in x.command:
            self.assertTrue(x.command[label] is not x_copy.command[label])
    
    def test_copying_attribute_that_some_other_depends_on_does_not_copy_the_dependency_relationship(self):
        x = self.fac.new("integer")
        y = self.fac.new("integer")
        def square(x:int)->int: return x*x
        y.add_dependency(Dependency(square),x)

        x.set(3)
        self.assertEqual(y.value,9)

        x_copy = x.copy()
        x_copy.set(4)
        self.assertEqual(y.value,9)


class Test_Setting_Multiple_Independent_Attributes_At_Once(unittest.TestCase):

    def test_set_multiple_attributes(self):
        fac = attribute_factory(Controller())
        x1 = fac.new('integer')
        x2 = fac.new('integer')
        message = fac.new('text')

        Attribute.set_multiple({x1:5, x2:-2, message:'XYZ'})
        Attribute.set_multiple({x1:10, x2:-15, message:'ABC'})
        self.assertEqual(x1.value,10)
        self.assertEqual(x2.value,-15)
        self.assertEqual(message.value, "ABC")

        fac.controller.undo()
        self.assertEqual(x1.value,5)
        self.assertEqual(x2.value,-2)
        self.assertEqual(message.value, "XYZ")
    
        fac.controller.redo()
        self.assertEqual(x1.value,10)
        self.assertEqual(x2.value,-15)
        self.assertEqual(message.value, "ABC")

        fac.controller.undo()
        self.assertEqual(x1.value,5)
        self.assertEqual(x2.value,-2)
        self.assertEqual(message.value, "XYZ")

    def test_dependent_attributes_are_ignored(self):
        fac = attribute_factory(Controller())
        x = fac.new('integer')
        y = fac.new('integer')
        z = fac.new('integer')
        x.set(2)
        y.set(0)
        z.set(0)
        def square(x:int)->int: return x*x
        y.add_dependency(square,x)

        self.assertEqual(y.value, 4)
        self.assertEqual(z.value, 0)
        Attribute.set_multiple({y:0, z:1})
        self.assertEqual(y.value, 4)
        self.assertEqual(z.value, 1)

    def test_setting_attributes_from_multiple_factories_with_different_controllers(self):
        fac1 = attribute_factory(Controller())
        fac2 = attribute_factory(Controller())
        x1 = fac1.new('integer')
        x2 = fac2.new('integer')
        Attribute.set_multiple({x1:0,x2:1})
        Attribute.set_multiple({x1:10,x2:8})
        self.assertEqual(x1.value,10)
        self.assertEqual(x2.value,8)
        fac1.controller.undo()
        self.assertEqual(x1.value,0)
        self.assertEqual(x2.value,8)
        fac2.controller.undo()
        self.assertEqual(x1.value,0)
        self.assertEqual(x2.value,1)


class Test_Attribute_Value_Formatting(unittest.TestCase):

    def test_real_attribute(self):
        fac = attribute_factory(Controller())
        x = fac.new('real')
        x.set(math.pi)
        self.assertEqual(x.value, math.pi)
        self.assertEqual(x.print(prec=2), '3.14')
        x.set(150.254)
        self.assertEqual(x.print(prec=0), '150')
        self.assertEqual(x.print(prec=5), '150.25400')

    def test_text_attribute(self):
        fac = attribute_factory(Controller())
        message = fac.new('text')
        message.set("Test text attribute")
        self.assertEqual(message.print(), "Test text attribute")

    def test_integer_attribute(self):
        fac = attribute_factory(Controller())
        i = fac.new('integer')
        i.set(8)
        self.assertEqual(i.print(), "8")

    def test_invalid_printop_raises_exception(self):
        fac = attribute_factory(Controller())
        x = fac.new('real')
        with self.assertRaises(Attribute.UnknownOption):
            x.print(invalid_option='__')

    def test_picking_nonexistent_format_option(self):
        fac = attribute_factory(Controller())
        x = fac.new('real')
        with self.assertRaises(Attribute.UnknownOption):
            x._pick_format_option('nonexistent_format_option', {})



class Test_Reading_Text_Attribute_Value_From_Text(unittest.TestCase):

    def test_any_string_can_be_read(self):
        fac = attribute_factory(Controller())
        attr = fac.new('text')
        attr.read("This is some random text.")
        self.assertEqual(attr.value, "This is some random text.")
        attr.read("")
        self.assertEqual(attr.value, "")


from src.core.attributes import Real_Attribute, Integer_Attribute
class Test_Reading_Integer_And_Real_Attribute_Value_From_Text(unittest.TestCase):

    def test_reading_integer_from_text(self):
        fac = attribute_factory(Controller())
        attr = fac.new("integer")
        self.__common_tests_for_int_and_real(attr)
        self.assertRaises(Integer_Attribute.CannotExtractInteger, attr.read, "")
        self.assertRaises(Integer_Attribute.CannotExtractInteger, attr.read, "   ")
        self.assertRaises(Integer_Attribute.CannotExtractInteger, attr.read, "asdfd ")

    def test_reading_real_from_text(self):
        fac = attribute_factory(Controller())
        attr = fac.new("real")
        self.__common_tests_for_int_and_real(attr)
        
        attr.read("0.001")
        self.assertEqual(attr.value, 0.001)
        attr.read("1e+21")
        self.assertEqual(attr.value, 1000000000000000000000)
        self.assertRaises(Real_Attribute.CannotExtractNumber, attr.read, "5/7")
        self.assertRaises(Real_Attribute.CannotExtractNumber, attr.read, " ")
        self.assertRaises(Real_Attribute.CannotExtractNumber, attr.read, "asdfd ")

    def __common_tests_for_int_and_real(self,attr:Attribute)->None:
        attr.read("789")
        self.assertEqual(attr.value, 789)
        attr.read("-78")
        self.assertEqual(attr.value, -78)
        attr.read("  -20   ")
        self.assertEqual(attr.value, -20)
        attr.read("  00001   ")
        self.assertEqual(attr.value, 1)
        attr.read("  1e03  ")
        self.assertEqual(attr.value, 1000)
        attr.read("  2e+03  ")
        self.assertEqual(attr.value, 2000)
        attr.read("  4000e-03  ")
        self.assertEqual(attr.value, 4)
        attr.read("  1000000000e-09  ")
        self.assertEqual(attr.value, 1)
        large_int = 2*10**100
        attr.read(f"  {large_int}e-100  ")
        self.assertEqual(attr.value, 2)




from src.core.attributes import Choice_Attribute
class Test_Choice_Attribute(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())
        self.c:Choice_Attribute = self.fac.choice()

    def test_setting_attribute_always_raises_excpetion_before_defining_options(self):
        self.assertRaises(self.c.OptionsNotDefined, self.c.set, " ")
        self.c.add_options("A", "B")
        self.c.set("A")

    def test_exception_is_raised_when_setting_to_nonexistent_option(self):
        self.c.add_options("A","B")
        self.assertRaises(Choice_Attribute.NonexistentOption, self.c.set, "C")

    def test_removing_options(self):
        self.c.add_options("A","B")
        self.c.remove_options("A")
        self.assertRaises(Choice_Attribute.NonexistentOption, self.c.set, "A")
        self.assertRaises(Choice_Attribute.NonexistentOption, self.c.remove_options, "A")

    def test_accessing_value_before_defining_options_raises_exception(self):
        with self.assertRaises(Choice_Attribute.OptionsNotDefined):
            self.c.value

    def test_currently_chosen_option_cannot_be_removed(self)->None:
        self.c.add_options("A","B")
        self.c.set("B")
        self.assertRaises(Choice_Attribute.CannotRemoveChosenOption, self.c.remove_options, "B")

    def test_print_options_as_a_tuple(self)->None:
        self.c.add_options(123, 456, 203)
        self.assertEqual(self.c.print_options(), ("123", "456", "203"))

    def test_check_value_is_in_options(self):
        self.c.add_options("A","B")
        self.assertTrue(self.c.is_option("A"))
        self.assertFalse(self.c.is_option("C"))


class Test_Duplicity_In_Added_Options_For_Choice_Attribute(unittest.TestCase):

    def test_duplicity_of_the_same_type_is_ignored(self):
        fac = attribute_factory(Controller())
        c = fac.choice()
        c.add_options(45, 56, 45, 78)
        self.assertEqual(c.print_options(),('45', '56', '78'))

    def test_duplicity_of_the_different_type_raises_exception(self):
        fac = attribute_factory(Controller())
        c = fac.choice()
        self.assertRaises(Choice_Attribute.DuplicateOfDifferentType, c.add_options, 45, 56, "45")

    def test_string_options_differing_in_trailing_and_leading_spaces_or_aggregated_spaces_are_considered_to_be_duplicates(self):
        fac = attribute_factory(Controller())
        c = fac.choice()
        c.add_options(
            "AA B", "AA    B", "   AA B   ", # these are considered to be identical
            "A AB",
        )
        self.assertEqual(c.print_options(),('AA B', 'A AB'))


class Test_Reading_Choice_From_Text(unittest.TestCase):

    def test_read_choice_from_text(self):
        fac = attribute_factory(Controller())
        c = fac.choice()
        c.add_options(45, 23, 78, "abc")
        c.read("45")
        self.assertEqual(c.value, 45)
        c.read("   78  ")
        self.assertEqual(c.value, 78)
        c.read("abc")
        self.assertEqual(c.value, "abc")


class Test_Make_Choice_Attribute_Dependent(unittest.TestCase):

    def test_choice_describing_result_of_comparison_of_two_integers(self):
        fac = attribute_factory(Controller())
        a = fac.new('integer', "a")
        b = fac.new('integer', "b")
        comp = fac.choice()
        comp.add_options("a is greater than b","a is equal to b","a is less than b")
        def comparison(a:int, b:int):
            if a>b: return "a is greater than b"
            elif a<b: return "a is less than b"
            else: return "a is equal to b"
        comp.add_dependency(comparison,a,b)
        a.set(5)
        b.set(7)
        self.assertEqual(comp.value, "a is less than b")
        a.set(8)
        b.set(1)
        self.assertEqual(comp.value, "a is greater than b")  
        # test the dependent choice can't be set manually
        comp.set("a is equal to b")
        self.assertEqual(comp.value, "a is greater than b")


import datetime
from src.core.attributes import Date_Attribute
import re
class Test_Date_Attribute(unittest.TestCase):

    def test_date_attribute(self):
        fac = attribute_factory(Controller())
        date = fac.new("date")
        date.set(datetime.date(2023,9,15))
        self.assertEqual(date.value, datetime.date(2023,9,15))
        self.assertEqual(date.print(locale_code='cs_cz'),"15.09.2023")
        self.assertEqual(date.print(locale_code='default'),"2023-09-15")
        self.assertEqual(date.print(),"2023-09-15")
        with self.assertRaises(Date_Attribute.UnknownLocaleCode):
            date.print(locale_code="!$_<>")

    def test_locale_code_is_not_case_sensitive(self):
        fac = attribute_factory(Controller())
        date = fac.new("date")
        date.set(datetime.date(2023,9,15))
        self.assertEqual(date.print(locale_code='cs_cz'),"15.09.2023")
        self.assertEqual(date.print(locale_code='CS_CZ'),"15.09.2023")
    
    def test_year_pattern(self):
        VALID_YEARS = ("2023", "1567", "2000", "0456")
        for y in VALID_YEARS:
            self.assertTrue(re.fullmatch(Date_Attribute.YEARPATT, y))
        INVALID_YEARS = ("sdf", "-456", "20000000", "20000", " ")
        for y in INVALID_YEARS:
            self.assertFalse(re.fullmatch(Date_Attribute.YEARPATT, y))

    def test_month_pattern(self):
        VALID_MONTHS = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
            '11', '12', '01', '02', '03', '04', '05', '06', '07', '08', '09']
        for m in VALID_MONTHS:
            self.assertTrue(re.fullmatch(Date_Attribute.MONTHPATT, m))
        INVALID_MONTHS = ('13', '0', '-2', '1000', "a", "00", "", "  ")
        for m in INVALID_MONTHS:
            self.assertFalse(re.fullmatch(Date_Attribute.MONTHPATT, m))  

    def test_day_pattern(self):
        VALID_DAYS = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', 
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', 
            '31', '01', '02', '03', '04', '05', '06', '07', '08', '09']
        for d in VALID_DAYS:
            self.assertTrue(re.fullmatch(Date_Attribute.DAYPATT, d))
        INVALID_DAYS =  ('32', '0', '-2', '1000', "a", "00", "", "  ")
        for d in INVALID_DAYS:
            self.assertFalse(re.fullmatch(Date_Attribute.DAYPATT, d))  

    def test_reading_date_from_string(self):
        fac = attribute_factory(Controller())
        date:Date_Attribute = fac.new("date")
        valid_examples = (
            "2023-9-15","2023,9,15", "2023-9-15", "2023_9_15", "2023_09_15",
            "15-9-2023","15,9,2023", "15.9.2023", "15_9_2023", "15_09_2023",
            "2023 - 9 - 15","2023 , 9 , 15", "2023 - 9 - 15", "2023 _ 9 _ 15", "2023 _ 09 _ 15"
        )
        for d in valid_examples:
            date.read(d)
            self.assertEqual(date.value,datetime.date(2023,9,15))

        invalid_examples = ("45661", "", "  ", "2023 9 15", "15..9.2023")
        for d in invalid_examples:
            self.assertRaises(Date_Attribute.CannotExtractDate,date.read,d)



from src.core.attributes import Monetary_Attribute, Decimal
class Test_Monetary_Attribute(unittest.TestCase):

    def test_defining_monetary_attribute_and_setting_its_value(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        mon.set(45)
        self.assertEqual(mon.value, 45)
        mon.set(45.12446656)
        self.assertEqual(mon.value, Decimal('45.12446656'))
        mon.set(-8)
        self.assertEqual(mon.value, -8)
        mon.set(0)
        self.assertEqual(mon.value,0)

        self.assertRaises(Attribute.InvalidValueType, mon.set, "45")
        self.assertRaises(Attribute.InvalidValueType, mon.set, "45 $")
        self.assertRaises(Attribute.InvalidValueType, mon.set, "$45")

    def test_currency_needs_to_be_specified_before_printing_money_value_as_a_string(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        mon.set(12)
        self.assertEqual(mon.print(locale_code="cs_cz", currency="USD"), "12,00 $")
        self.assertEqual(mon.print(locale_code="en_us", currency="USD"), "$12.00")
        self.assertEqual(mon.print(locale_code="cs_cz", currency="JPY"), "12 ¥")
        self.assertEqual(mon.print(locale_code="cs_cz", currency="USD", zero_decimals=False), "12 $")

        mon.set(11.5)
        self.assertEqual(mon.print(locale_code="cs_cz", currency="USD"), "11,50 $")
        self.assertEqual(mon.print(locale_code="en_us", currency="USD"), "$11.50")
        self.assertEqual(mon.print(locale_code="cs_cz", currency="JPY"), "12 ¥")
        self.assertEqual(mon.print(locale_code="cs_cz", currency="USD", zero_decimals=False), "11,50 $")

    def test_bankers_rounding_is_correctly_used(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        mon.set(12.5) 
        self.assertEqual(mon.print(locale_code="cs_cz", currency="JPY"), "12 ¥")

        mon.set(1.455)
        self.assertEqual(mon.print(locale_code="en_us", currency="USD"), "$1.46")
        mon.set(1.445)
        self.assertEqual(mon.print(locale_code="en_us", currency="USD"), "$1.44")
        mon.set(0.001)
        self.assertEqual(mon.print(locale_code="en_us", currency="USD"), "$0.00")

    def test_sign_is_always_put_right_on_the_beginning_of_the_string(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        mon.set(-5.01)
        self.assertEqual(mon.print(locale_code="en_us", currency="USD"), "-$5.01")
        self.assertEqual(mon.print(locale_code="cs_cz", currency="USD"), "-5,01 $")

    def test_plus_sign_can_be_enforced(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        mon.set(8.45)
        self.assertEqual(mon.print(locale_code="en_us", currency="USD", enforce_plus=True), "+$8.45")

    def test_raise_exception_on_invalid_locale_code_or_currency_value(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        mon.set(8.45)
        with self.assertRaises(Monetary_Attribute.UndefinedCurrencySymbol):
            mon.print(locale_code="en_us", currency="!$X")
        with self.assertRaises(Monetary_Attribute.UnknownLocaleCode):
            mon.print(locale_code="!$_<>", currency="USD")

    def test_reading_monetary_value_from_string(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        mon.read("$20")
        self.assertEqual(mon.value, Decimal('20'))
        mon.read("$20.561")
        self.assertEqual(mon.value, Decimal('20.561'))
        mon.read("$14,561")
        self.assertEqual(mon.value, Decimal('14.561'))
        mon.read("$0,561")
        self.assertEqual(mon.value, Decimal('0.561'))
        mon.read("$5,")
        self.assertEqual(mon.value, Decimal('5'))

        mon.read("20 $")
        self.assertEqual(mon.value, Decimal('20'))
        mon.read("15$")
        self.assertEqual(mon.value, Decimal('15'))
        mon.read("14\t$")
        self.assertEqual(mon.value, Decimal('14'))
        mon.read("20.561 $")
        self.assertEqual(mon.value, Decimal('20.561'))
        mon.read("14,561 $")
        self.assertEqual(mon.value, Decimal('14.561'))
        mon.read("45,12 Kč")
        self.assertEqual(mon.value, Decimal('45.12'))

        INVALID_VALUES = (
            "", "  ", 
            "20", "20.561", #missing currency symbol
        )
        for value in INVALID_VALUES:
            self.assertRaises(Monetary_Attribute.CannotExtractValue, mon.read, value)
        
        UNKNOWN_SYMBOLS = (
            "20 A", "20 klm", "25 $$", "$$45"
        )
        for value in UNKNOWN_SYMBOLS:
            self.assertRaises(Monetary_Attribute.UndefinedCurrencySymbol, mon.read, value)

    def test_monetary_attribute_validation(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money")
        self.assertTrue(mon.is_valid(1))
        self.assertTrue(mon.is_valid(1.56))
        self.assertTrue(mon.is_valid(-45))
        self.assertTrue(mon.is_valid(0))
        self.assertTrue(mon.is_valid(5/7))
        self.assertTrue(mon.is_valid(math.e))

        self.assertFalse(mon.is_valid(""))
        self.assertFalse(mon.is_valid("  "))
        self.assertFalse(mon.is_valid("asdf"))
        self.assertFalse(mon.is_valid("$"))
        self.assertFalse(mon.is_valid("20 $"))
        self.assertFalse(mon.is_valid("$ 20"))
        self.assertFalse(mon.is_valid("20"))
        self.assertFalse(mon.is_valid("20.45"))
        self.assertFalse(mon.is_valid("-45"))



if __name__=="__main__": unittest.main()