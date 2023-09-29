from __future__ import annotations

import sys 
sys.path.insert(1,"src")


import unittest
import dataclasses
from typing import Any

from src.core.attributes import attribute_factory, Attribute, Set_Attr_Data, UnknownLocaleCode, NBSP
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

    def test_setting_initial_value_of_attribute(self)->None:
        a = self.attrfac.new('integer',5)
        self.assertEqual(a.value, 5)

    def test_name_of_attribute_has_to_be_of_type_string(self)->None:
        self.assertRaises(Attribute.Invalid_Name, self.attrfac.new, name=666)
        x = self.attrfac.new(name="Valid name")
        self.assertRaises(Attribute.Invalid_Name, x.rename, name=666)

    def test_setting_attribute_to_invalid_type_raises_error(self)->None:
        self.assertRaises(Attribute.InvalidAttributeType, self.attrfac.new, 'invalid_argument_type_0123456789')

    def test_accessing_attribute_value(self)->None:
        a = self.attrfac.new('text')
        a.value
    
    def test_setting_the_attribute_value(self)->None:
        a = self.attrfac.new('text',"Some text.")
        self.assertEqual(a.value, "Some text.")

    def test_valid_value(self)->None:
        a = self.attrfac.new('integer')
        self.assertTrue(a.is_valid(5))
        self.assertRaises(Attribute.InvalidValueType, a.is_valid, 0.5)
        self.assertRaises(Attribute.InvalidValueType, a.is_valid, "abc")
        self.assertRaises(Attribute.InvalidValueType, a.is_valid, "5")
        self.assertRaises(Attribute.InvalidValueType, a.is_valid, "")

    def test_for_text_attribute_any_string_value_is_valid(self):
        a = self.attrfac.new('text')
        self.assertRaises(Attribute.InvalidValueType, a.is_valid, 5)
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

        self.assertRaises(Attribute.InvalidValueType, x.is_valid, None)
        self.assertRaises(Attribute.InvalidValueType, x.is_valid, "")
        self.assertRaises(Attribute.InvalidValueType, x.is_valid, " ")
        self.assertRaises(Attribute.InvalidValueType, x.is_valid, "5")
        self.assertRaises(Attribute.InvalidValueType, x.is_valid, "0.5")
        self.assertRaises(Attribute.InvalidValueType, x.is_valid, "a")
        self.assertRaises(Attribute.InvalidValueType, x.is_valid, complex(1,2))
        self.assertRaises(Attribute.InvalidValueType, x.is_valid, complex(1,0))



from src.core.attributes import Attribute_Factory, Number_Attribute
class Test_Defining_Custom_Attribute_Type(unittest.TestCase):

    class Positive_Integer_Attribute(Number_Attribute):
        default_value = 1
        def _check_input_type(self, value: Any)->None:
            try: 
                if not value==int(value): raise
            except: 
                raise Attribute.InvalidValueType(type(value))

        def _is_value_valid(self, value: Any) -> bool:
            return value>0
            
        def print(self,*options)->str: # pragma: no cover
            return str(self._value)
            
        def read(self,text:str)->None: # pragma: no cover
            pass
            
    def test_defining_positive_integer_attribute(self):
        attrfac = attribute_factory(Controller())
        attrfac.add('positive integer', self.Positive_Integer_Attribute)
        attr = attrfac.new('positive integer', 5)
        self.assertEqual(attr.value, 5)
        self.assertFalse(attr.is_valid(0))
        self.assertFalse(attr.is_valid(-1))
        self.assertRaises(Attribute.InvalidValueType, attr.is_valid, "abc")
        self.assertRaises(Attribute.InvalidValueType, attr.is_valid, 0.5)
        self.assertRaises(Attribute.InvalidValue, attr.set, 0)
        self.assertRaises(Attribute.InvalidValue, attr.set, -1)
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
        attr:AbstractAttribute

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
        volume = fac.new('integer', name='volume')
        def  write_to_logbook(data:Set_Attr_Data)->Test_Undo_And_Redo_Setting_Attribute_Values.Write_Value_To_LogBook:
            write_data = self.Write_Data(logbook,data.attr)
            return self.Write_Value_To_LogBook(write_data)
        volume.on_set('test',write_to_logbook,'post')
        volume.set(5)
        volume.set(10)
        self.assertEqual(volume.value,10)

        fac.undo()
        self.assertEqual(volume.value,5)
        fac.redo()
        self.assertEqual(volume.value,10)


from src.core.attributes import Dependency
class Test_Dependent_Attributes(unittest.TestCase):
    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())

    def test_setting_up_dependency(self):
        DENSITY = 1000
        volume = self.fac.new('integer', name="volume")
        mass = self.fac.new('integer', name="mass")
        def dependency(volume:int)->int:
            return volume*DENSITY
        
        mass.add_dependency(dependency, volume)

        volume.set(2)
        self.assertEqual(mass.value, 2000)

        volume.set(5)
        self.assertEqual(mass.value, 5000)

        self.fac.undo()
        self.assertEqual(mass.value, 2000)
        self.fac.redo()
        self.assertEqual(mass.value, 5000)
        self.fac.undo()
        self.assertEqual(mass.value, 2000)

    def test_dependency_has_to_have_at_least_one_input(self):
        y = self.fac.new('integer')
        def foo()->int: return 4 # pragma: no cover
        self.assertRaises(Dependency.NoInputs, y.add_dependency, foo)

    def test_chaining_dependency_of_three_attributes(self):
        side = self.fac.new('integer', name='side')
        volume = self.fac.new('integer', name='volume')
        max_n_of_items = self.fac.new('integer', name='max number of items')

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

        self.fac.undo()
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)
        self.fac.redo()
        self.assertEqual(volume.value,8)
        self.assertEqual(max_n_of_items.value,80)
        self.fac.undo()
        self.assertEqual(volume.value,1)
        self.assertEqual(max_n_of_items.value,10)

    def test_adding_second_dependency_raises_exception(self):
        x = self.fac.new('integer',name='x')
        y = self.fac.new('integer',name='y')
        def x_squared(x:int)->int: return x*x # pragma: no cover
        y.add_dependency(x_squared,x)
        self.assertRaises(Attribute.DependencyAlreadyAssigned, y.add_dependency, x_squared,x)
        # after breaking dependency, it is possible to reassign new dependency
        y.break_dependency()
        y.add_dependency(x_squared,x)
        self.assertRaises(Attribute.DependencyAlreadyAssigned, y.add_dependency, x_squared,x)

    def test_calling_set_method_on_dependent_attribute_has_no_effect(self)->None:
        a = self.fac.new('integer',name='a')
        b = self.fac.new('integer', name='b')
        def b_double_of_a(a:int)->int: 
            return 2*a
        b.add_dependency(b_double_of_a, a)
        
        a.set(2)
        self.assertEqual(b.value,4)
        b.set(2)
        self.assertEqual(b.value,4)

    def test_removing_dependency(self)->None:
        a = self.fac.new('integer',name='a')
        b = self.fac.new('integer', name='b')
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
        a = self.fac.new('integer', name='a')
        def triple(a:int)->int:  # pragma: no cover
            return 2*a
        self.assertRaises(Dependency.CyclicDependency, a.add_dependency, triple, a)

    def test_attribute_indirectly_depending_on_itself_raises_exception(self):
        a = self.fac.new('integer', name='a')
        b = self.fac.new('integer', name='b')
        c = self.fac.new('integer', name='c')
        def equal_to(x:int)->int: # pragma: no cover
            return x
        a.add_dependency(equal_to,b)
        b.add_dependency(equal_to,c)
        with self.assertRaises(Dependency.CyclicDependency):
            c.add_dependency(equal_to, a)

    def test_dependent_attribute_is_updated_immediatelly_after_adding_the_dependency(self):
        x = self.fac.new('integer',name='x')
        x.set(2)
        y = self.fac.new('integer',name='y')
        y.set(0)
        def double(x:int)->int: return 2*x

        self.assertEqual(y.value,0)
        y.add_dependency(double,x)
        self.assertEqual(y.value,4)

    def test_breaking_dependency_of_independent_attribute_raises_exception(self):
        independent_attribute = self.fac.new('integer',name='x')
        self.assertRaises(Attribute.NoDependencyIsSet, independent_attribute.break_dependency)


class Test_Correspondence_Between_Dependency_And_Attributes(unittest.TestCase):

    def test_assigning_invalid_attribute_type_for_dependency_function_argument_raises_exception(self):
        fac = Attribute_Factory(Controller())
        x = fac.new('text',name="x")
        y = fac.new('integer',name="y")
        def y_of_x(x:int)->int: return x*x # pragma: no cover
        with self.assertRaises(Dependency.WrongAttributeTypeForDependencyInput):
            y.add_dependency(y_of_x,x)

    def test_adding_dependency_with_return_type_not_matching_the_dependent_attribute_raises_exception(self):
        fac = Attribute_Factory(Controller())
        x = fac.new('integer',name="x")
        y = fac.new('text',name="y")
        def y_of_x(x:int)->int: return x*x # pragma: no cover
        with self.assertRaises(Attribute.InvalidValueType):
            y.add_dependency(y_of_x,x)


import math
class Test_Using_Dependency_Object_To_Handle_Invalid_Input_Values(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = Attribute_Factory(Controller())
    
    def test_raise_exception_when_using_attribute_with_incorrect_type(self):
        x = self.fac.new('text',name="x")
        y = self.fac.new('integer',name="y")
        def y_of_x(x:int)->int: return x*x # pragma: no cover
        with self.assertRaises(Dependency.WrongAttributeTypeForDependencyInput):
            y.add_dependency(y_of_x,x)

    def test_handle_input_outside_of_the_function_domain_in_dependent_attribute_calculation(self):
        x = self.fac.new('integer',name="x")
        y = self.fac.new('real',name="y")
        def y_of_x(x:int)->float: return math.sqrt(x) # pragma: no cover
        y.add_dependency(y_of_x,x)
        x.set(-1)
        self.assertTrue(math.isnan(y.value))

    def test_handle_input_outside_of_the_function_when_adding_the_dependency(self):
        x = self.fac.new('integer', -1, name="x")
        y = self.fac.new('real', name="y")

        def y_of_x(x:int)->float: return math.sqrt(x) # pragma: no cover
        y.add_dependency(y_of_x,x)
        self.assertTrue(math.isnan(y.value))

    def test_division_by_zero(self)->None:
        x = self.fac.new('real', 0, name="x")
        y = self.fac.new('real',name="y")

        def y_of_x(x:float)->float: return 1/x 
        y.add_dependency(y_of_x,x)
        self.assertTrue(math.isnan(y.value))


class Test_Copying_Attribute(unittest.TestCase):

    def setUp(self)->None:
        self.fac = attribute_factory(Controller())

    def test_copy_independent_attribute(self)->None:
        x = self.fac.new("integer", 5, name='x')

        self.assertEqual(x.value, 5)
        x_copy = x.copy()
        self.assertEqual(x_copy.value, 5)
        self.assertEqual(x_copy.type, 'integer')
        self.assertTrue(x_copy.id != x.id)
    
    def test_copying_the_attribute_does_not_copy_its_dependencies(self)->None:
        x = self.fac.new("integer", 1, name='x')
        y = self.fac.new("integer", name='y')
        def double(x:int)->int: return 2*x

        y.add_dependency(double,x)

        self.assertListEqual(y.dependency.inputs,[x])
        y_copy = y.copy()

        x.set(2)
        self.assertEqual(y.value,4)
        self.assertEqual(y_copy.value,2)
 


    @dataclasses.dataclass
    class Message:
        text:str = ""

    @dataclasses.dataclass
    class Write_Value_To_Message_Text_Data:
        attr:Attribute
        message:Test_Copying_Attribute.Message
    
    @dataclasses.dataclass
    class Write_Value_To_Message_Text(Command):
        data:Test_Copying_Attribute.Write_Value_To_Message_Text_Data
        prev_text:str = dataclasses.field(init=False)
        new_text:str = dataclasses.field(init=False)
        def run(self):
            self.prev_text = self.data.message.text
            self.data.message.text = str(self.data.attr.value)
            self.new_text = self.data.message.text
        def undo(self): # pragma: no cover
            self.data.message.text = self.prev_text
        def redo(self): # pragma: no cover
            self.data.message.text = self.new_text

    def test_copying_the_attribute_does_not_copy_those_commands_added_after_the_original_attribute_initialization(self):
        x = self.fac.new("integer", 2, name='x')
        message = self.Message()
        def write_value_to_message_txt(data:Set_Attr_Data)->Test_Copying_Attribute.Write_Value_To_Message_Text:
            return self.Write_Value_To_Message_Text(self.Write_Value_To_Message_Text_Data(x,message))
        x.command['set'].add('test',write_value_to_message_txt,'post')

        x_copy = x.copy()
        x.set(5)
        self.assertEqual(message.text,"5")
        x_copy.set(511651654547)
        self.assertEqual(message.text,"5")

    def test_attribute_basic_commands_are_not_identical_to_those_of_its_copy(self):
        x = self.fac.new("integer", name='x')
        x_copy = x.copy()
        for label in x.command:
            self.assertTrue(x.command[label] is not x_copy.command[label])
    
    def test_copying_attribute_that_some_other_depends_on_does_not_copy_the_dependency_relationship(self):
        x = self.fac.new("integer")
        y = self.fac.new("integer")
        def square(x:int)->int: return x*x
        y.add_dependency(square,x)

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

        fac.undo()
        self.assertEqual(x1.value,5)
        self.assertEqual(x2.value,-2)
        self.assertEqual(message.value, "XYZ")
    
        fac.redo()
        self.assertEqual(x1.value,10)
        self.assertEqual(x2.value,-15)
        self.assertEqual(message.value, "ABC")

        fac.undo()
        self.assertEqual(x1.value,5)
        self.assertEqual(x2.value,-2)
        self.assertEqual(message.value, "XYZ")

    def test_dependent_attributes_are_ignored(self):
        fac = attribute_factory(Controller())
        x = fac.new('integer',2)
        y = fac.new('integer',0)
        z = fac.new('integer',0)

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
        x = fac.new('real', math.pi)
        self.assertEqual(x.value, Decimal(str(math.pi)))
        self.assertEqual(x.print(precision=2), '3.14')
        x.set(150.254)
        self.assertEqual(x.print(precision=0), '150')
        self.assertEqual(x.print(precision=5), '150.25400')

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
        self.assertRaises(Integer_Attribute.CannotExtractInteger, attr.read, "1.25")

    def test_reading_real_from_text(self):
        fac = attribute_factory(Controller())
        attr = fac.new("real")
        self.__common_tests_for_int_and_real(attr)
        
        attr.read("0.001")
        self.assertEqual(attr.value, Decimal(str(0.001)))
        attr.read("1e+21")
        self.assertEqual(attr.value, 1000000000000000000000)
        attr.read("04e-05")
        self.assertEqual(attr.value, Decimal(str(0.00004)))
        attr.read("-04e-05")
        self.assertEqual(attr.value, Decimal(str(-0.00004)))
        attr.read("+05e-05")
        self.assertEqual(attr.value, Decimal(str(0.00005)))
        attr.read("+01E-02")
        self.assertEqual(attr.value, Decimal(str(0.01)))

        self.assertRaises(Real_Attribute.CannotExtractReal, attr.read, "5/7")
        self.assertRaises(Real_Attribute.CannotExtractReal, attr.read, " ")
        self.assertRaises(Real_Attribute.CannotExtractReal, attr.read, "asdfd ")

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
        attr.read("  1.564e+03  ")
        self.assertEqual(attr.value, 1564)
        attr.read("  1,564e+03  ")
        self.assertEqual(attr.value, 1564)


class Test_Printing_Real_Attribute_Value(unittest.TestCase):

    def test_printing_real_value(self):
        fac = attribute_factory(Controller())
        attr = fac.new("real", 5.3)
        self.assertEqual(attr.print(trailing_zeros=False), "5.3")
        self.assertEqual(attr.print(precision=5), "5.30000")

        attr.set(5.45)
        self.assertEqual(attr.print(precision=1), "5.4")
        attr.set(5.55)
        self.assertEqual(attr.print(precision=1), "5.6")

    def test_printing_real_values_with_locale_code_specified(self):
        fac = attribute_factory(Controller())
        attr = fac.new("real", 5.3)
        self.assertEqual(attr.print(locale_code="cs_cz",trailing_zeros=False), "5,3")
        attr.set(5)
        self.assertEqual(attr.print(locale_code="cs_cz",trailing_zeros=False), "5")
        attr.set(0.0)
        self.assertEqual(attr.print(locale_code="cs_cz",trailing_zeros=False), "0")

    def test_is_int(self)->None:
        self.assertTrue(Real_Attribute.is_int(12.0))
        self.assertTrue(Real_Attribute.is_int(0.0))
        self.assertTrue(Real_Attribute.is_int(-1))
        self.assertTrue(Real_Attribute.is_int(math.pi-math.pi))

        self.assertFalse(Real_Attribute.is_int(12.1))
        self.assertFalse(Real_Attribute.is_int(math.pi))
        self.assertFalse(Real_Attribute.is_int(-12.1))


class Test_Thousands_Separator(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())

    def test_thousands_separator_for_integers(self):
        attr = self.fac.new("integer")
        attr.set(12000)
        self.assertEqual(attr.print(use_thousands_separator=True), f'12{NBSP}000')
        attr.set(1000)
        self.assertEqual(attr.print(use_thousands_separator=True), f'1{NBSP}000')
        attr.set(10000000)
        self.assertEqual(attr.print(use_thousands_separator=True), f'10{NBSP}000{NBSP}000') 

    def test_thousands_separator_for_reals(self):
        attr = self.fac.new("real")

        attr.set(12000)
        self.assertEqual(attr.print(use_thousands_separator=True, trailing_zeros=False), f'12{NBSP}000')
        attr.set(1000)
        self.assertEqual(attr.print(use_thousands_separator=True, trailing_zeros=False), f'1{NBSP}000')
        attr.set(10000000)
        self.assertEqual(attr.print(use_thousands_separator=True, trailing_zeros=False), f'10{NBSP}000{NBSP}000') 

        attr.set(12000.00505)
        self.assertEqual(attr.print(use_thousands_separator=True, trailing_zeros=False), f'12{NBSP}000.00505')

        attr.set(12000.000)
        self.assertEqual(attr.print(precision=5, use_thousands_separator=True), f'12{NBSP}000.00000')


class Test_Reading_Value_With_Space_As_Thousands_Separator(unittest.TestCase):

    def test_reading_value_with_space_as_thousands_separator(self):
        fac = attribute_factory(Controller())
        attr = fac.new("real")
        attr.read("12 000")
        self.assertEqual(attr.value, 12000)
        attr.read(f"100{NBSP}000")
        self.assertEqual(attr.value, 100000)
        attr.read(f"-15\t000")
        self.assertEqual(attr.value, -15000)
        attr.read(f"4 230.560")
        self.assertEqual(attr.value, Decimal('4230.560'))


from src.core.attributes import Choice_Attribute
class Test_Choice_Attribute(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())
        self.c:Choice_Attribute = self.fac.choice()

    def test_zeroth_option_is_selected_if_attribute_initially_contains_no_options(self):
        self.c.add_options("A","B","C")
        self.assertEqual(self.c.value, "A")
        self.c.add_options("C", "D")
        self.assertEqual(self.c.value, "A")

    def test_setting_attribute_always_raises_exception_before_defining_options(self):
        self.assertRaises(self.c.NoOptionsAvailable, self.c.set, " ")
        self.c.add_options("A", "B")
        self.c.set("A")

    def test_exception_is_raised_when_setting_to_nonexistent_option(self):
        self.c.add_options("A","B")
        self.assertRaises(Choice_Attribute.UndefinedOption, self.c.set, "C")

    def test_removing_options(self):
        self.c.add_options("A","B")
        self.c.remove_options("B")
        self.assertRaises(Choice_Attribute.UndefinedOption, self.c.set, "B")
        self.assertRaises(Choice_Attribute.UndefinedOption, self.c.remove_options, "B")

    def test_accessing_value_before_defining_options_raises_exception(self):
        with self.assertRaises(Choice_Attribute.NoOptionsAvailable):
            self.c.value

    def test_currently_chosen_option_cannot_be_removed(self)->None:
        self.c.add_options("A","B")
        self.c.set("B")
        self.assertRaises(Choice_Attribute.CannotRemoveChosenOption, self.c.remove_options, "B")

    def test_print_options_as_a_tuple(self)->None:
        self.c.add_options(123, 456, 203)
        self.assertEqual(self.c.print_options(), ("123", "456", "203"))
        self.c.clear_options()
        self.c.add_options("America", "Europe", "Antarctica")
        self.assertEqual(self.c.print_options(), ("America", "Europe", "Antarctica"))
        self.assertEqual(self.c.print_options(lower_case=True), ("america", "europe", "antarctica"))

    def test_check_value_is_in_options(self):
        self.c.add_options("A","B")
        self.assertTrue(self.c.is_option("A"))
        self.assertFalse(self.c.is_option("C"))

    def test_printing_single_options(self):
        self.c.add_options("A","B")
        self.assertTrue(self.c.print(lower_case=True),"A")


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
        self.assertRaises(Choice_Attribute.UndefinedOption, c.read, "not an option")


class Test_Make_Choice_Attribute_Dependent(unittest.TestCase):

    def test_choice_describing_result_of_comparison_of_two_integers(self):
        fac = attribute_factory(Controller())
        a = fac.new('integer', name="a")
        b = fac.new('integer', name="b")
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
        date = fac.new("date", datetime.date(2023,9,15))
        self.assertEqual(date.value, datetime.date(2023,9,15))
        self.assertEqual(date.print(locale_code='cs_cz'),"15.09.2023")
        self.assertEqual(date.print(locale_code='en_us'),"2023-09-15")
        self.assertEqual(date.print(),"2023-09-15")
        with self.assertRaises(UnknownLocaleCode):
            date.print(locale_code="!$_<>")
        self.assertRaises(Attribute.InvalidValueType, date.set, "132135561")

    def test_locale_code_is_not_case_sensitive(self):
        fac = attribute_factory(Controller())
        date = fac.new("date", datetime.date(2023,9,15))
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
        mon:Monetary_Attribute = fac.new("money", 45)
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
        mon:Monetary_Attribute = fac.new("money", 12)
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="USD"), f"12,00{NBSP}$")
        self.assertEqual(mon.print(locale_code="en_us", currency_code="USD"), "$12.00")
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="JPY"), f"12{NBSP}¥")
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="USD", trailing_zeros=False), f"12{NBSP}$")

        mon.set(11.5)
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="USD"), f"11,50{NBSP}$")
        # the locale code is not case sensitive
        self.assertEqual(mon.print(locale_code="CS_cz", currency_code="USD"), f"11,50{NBSP}$")
        self.assertEqual(mon.print(locale_code="en_us", currency_code="USD"), "$11.50")
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="JPY"), f"12{NBSP}¥")
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="USD", trailing_zeros=False), f"11,50{NBSP}$")

    def test_bankers_rounding_is_correctly_used(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money", 12.5)
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="JPY"), f"12{NBSP}¥")

        mon.set(1.455)
        self.assertEqual(mon.print(locale_code="en_us", currency_code="USD"), "$1.46")
        mon.set(1.445)
        self.assertEqual(mon.print(locale_code="en_us", currency_code="USD"), "$1.44")
        mon.set(0.001)
        self.assertEqual(mon.print(locale_code="en_us", currency_code="USD"), "$0.00")

    def test_sign_is_always_put_right_on_the_beginning_of_the_string(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money", -5.01)
        self.assertEqual(mon.print(locale_code="en_us", currency_code="USD"), "-$5.01")
        self.assertEqual(mon.print(locale_code="cs_cz", currency_code="USD"), f"-5,01{NBSP}$")

    def test_plus_sign_can_be_enforced(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money", 8.45)
        self.assertEqual(mon.print(locale_code="en_us", currency_code="USD", enforce_plus=True), "+$8.45")

    def test_raise_exception_on_invalid_locale_code_or_currency_value(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money", 8.45)
        with self.assertRaises(Monetary_Attribute.CurrencyNotDefined):
            mon.print(locale_code="en_us", currency_code="!$X")
        with self.assertRaises(UnknownLocaleCode):
            mon.print(locale_code="!$_<>", currency_code="USD")

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
        mon.read("-$5,")
        self.assertEqual(mon.value, Decimal('-5'))
        mon.read("+$5,")
        self.assertEqual(mon.value, Decimal('5'))

        mon.read("20 $")
        self.assertEqual(mon.value, Decimal('20'))
        mon.read(f"28{NBSP}$")
        self.assertEqual(mon.value, Decimal('28'))
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
        mon.read("+45,12 Kč")
        self.assertEqual(mon.value, Decimal('45.12'))
        mon.read("-45,12 Kč")
        self.assertEqual(mon.value, Decimal('-45.12'))

        self.assertRaises(Monetary_Attribute.ReadingBlankText, mon.read, "  ")
        INVALID_VALUES = (
            "20", "20.561", #missing currency symbol
        )
        for value in INVALID_VALUES:
            self.assertRaises(Monetary_Attribute.CannotExtractValue, mon.read, value)
        
        UNKNOWN_SYMBOLS = (
            "20 A", "20 klm", "25 $$", "$$45"
        )
        for value in UNKNOWN_SYMBOLS:
            self.assertRaises(Monetary_Attribute.UnknownCurrencySymbol, mon.read, value)

    def test_monetary_attribute_validation(self):
        fac = attribute_factory(Controller())
        mon = fac.new("money")
        self.assertTrue(mon.is_valid(1))
        self.assertTrue(mon.is_valid(1.56))
        self.assertTrue(mon.is_valid(-45))
        self.assertTrue(mon.is_valid(0))
        self.assertTrue(mon.is_valid(5/7))
        self.assertTrue(mon.is_valid(math.e))
        self.assertTrue(mon.is_valid(math.nan))

        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "  ")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "asdf")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "$")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "20 $")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "$ 20")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "20")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "20.45")
        self.assertRaises(Attribute.InvalidValueType, mon.is_valid, "-45")


    def test_print_with_space_as_thousands_separator(self):
        fac = attribute_factory(Controller())
        mon:Monetary_Attribute = fac.new("money", 4100300)

        self.assertEqual(
            mon.print(
                use_thousands_separator=True,
                locale_code="en_us", 
                currency_code="USD",
                trailing_zeros=False
            ), 
            f"$4{NBSP}100{NBSP}300"
        )

        mon.set(0)
        self.assertEqual(
            mon.print(
                use_thousands_separator=True,
                locale_code="en_us", 
                currency_code="USD",
                trailing_zeros=False
            ), 
            f"$0"
        )

        mon.set(-4100300)
        self.assertEqual(
            mon.print(
                use_thousands_separator=True,
                locale_code="en_us", 
                currency_code="USD",
                trailing_zeros=False
            ), 
            f"-$4{NBSP}100{NBSP}300"
        )


class Test_Reading_Monetary_Value_With_Space_As_Thousands_Separator(unittest.TestCase):

    def test_reading_value_with_space_as_thousands_separator(self):
        fac = attribute_factory(Controller())
        attr = fac.new("money")
        attr.read("12 000 $")
        self.assertEqual(attr.value, 12000)
        attr.read(f"100{NBSP}000 $")
        self.assertEqual(attr.value, 100000)
        attr.read(f"-$15\t000")
        self.assertEqual(attr.value, -15000)



from src.core.attributes import Attribute_List
class Test_Attribute_List(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())

    def test_attribute_list_type_can_be_initially_set_to_any_valid_type_of_attribute(self):
        valid_types = self.fac.types.keys()
        for atype in valid_types:
            self.fac.newlist(atype)

    def test_creating_attribute_list_with_invalid_attribute_type_raises_exception(self):
        self.assertRaises(Attribute.InvalidAttributeType, self.fac.newlist, 'dsafgarga')

    def test_attribute_list_is_initially_empty_if_no_item_was_initially_specified(self):
        alist = self.fac.newlist('text')
        self.assertListEqual(alist.attributes, [])
    
    def test_only_attribute_with_type_specified_by_list_can_be_added(self):
        alist = self.fac.newlist('text')
        attr = self.fac.new('text')
        alist.append(attr)
        self.assertListEqual(alist.attributes, [attr])
        int_attr = self.fac.new('integer')
        self.assertRaises(Attribute_List.WrongAttributeType, alist.append, int_attr)

    def test_attributes_can_be_added_at_the_list_initialization(self):
        alist = self.fac.newlist("text", ["xyz"])
        self.assertEqual(len(alist.attributes), 1)
        self.assertEqual(alist.attributes[-1].value,"xyz")

    def test_removing_attributes(self):
        alist = self.fac.newlist("integer", [0])
        some_attr = alist[-1]
        alist.remove(some_attr)
        # removing already removed item raises exception
        self.assertRaises(Attribute_List.NotInList, alist.remove, some_attr)

    def test_looping_over_attributes(self):
        alist = self.fac.newlist("integer", [0,2,3])
        values = []
        for a in alist:
            values.append(a.value)
        self.assertListEqual(values, [0,2,3])


from src.core.attributes import AbstractAttribute
class Test_Undo_And_Redo_Editing_The_Attribute_List(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())
        self.alist = self.fac.newlist("integer")

    def test_undo_adding_item_to_the_list(self):
        attr = self.fac.new("integer", name="theattr")
        self.alist.append(attr)

        self.fac.undo()
        self.assertListEqual(self.alist.attributes, [])
        self.fac.redo()
        self.assertListEqual(self.alist.attributes, [attr])
        self.fac.undo()
        self.assertListEqual(self.alist.attributes, [])

    def test_undo_removing_item_from_the_list(self):
        attr = self.fac.new("integer")
        self.alist.append(attr)

        self.alist.remove(attr)
        self.fac.undo()
        self.assertListEqual(self.alist.attributes, [attr])
        self.fac.redo()
        self.assertListEqual(self.alist.attributes, [])
        self.fac.undo()
        self.assertListEqual(self.alist.attributes, [attr])


class Test_Attribute_List_Set_Method(unittest.TestCase): 

    @dataclasses.dataclass
    class Set_Cmd_Call_Counter:
        count:int = 0

    @dataclasses.dataclass
    class Increment_Attr(Command):
        counter:Test_Attribute_List_Set_Method.Set_Cmd_Call_Counter
        def run(self): 
            self.counter.count += 1
        def undo(self): 
            self.counter.count -= 1
        def redo(self): 
            self.counter.count += 1

    def __attr_cmd(self,data:Set_Attr_Data)->Increment_Attr:
        return self.Increment_Attr(self.set_calls_counter)


    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())
        self.alist = self.fac.newlist("integer")
        self.set_calls_counter = self.Set_Cmd_Call_Counter(count=0)
        self.alist.on_set('test',self.__attr_cmd,'post')

    def test_running_command_on_calling_set_method_of_attribute_list(self)->None:
        self.assertEqual(self.set_calls_counter.count,0)
        self.alist.set()
        self.assertEqual(self.set_calls_counter.count,1)
        self.fac.undo()
        self.assertEqual(self.set_calls_counter.count,0)
        self.fac.redo()
        self.assertEqual(self.set_calls_counter.count,1)
        self.fac.undo()
        self.assertEqual(self.set_calls_counter.count,0)

    def test_setting_value_of_attribute_in_list_runs_set_command_of_the_attribute_list(self):
        new_attr = self.fac.new("integer")
        self.alist.append(new_attr)

        self.set_calls_counter.count = 0
        self.alist.set()
        self.assertEqual(self.set_calls_counter.count, 1)
        new_attr.set(5)
        self.assertEqual(self.set_calls_counter.count, 2)
        new_attr.set(7)
        self.assertEqual(self.set_calls_counter.count, 3)
        self.alist.factory.undo()
        self.assertEqual(self.set_calls_counter.count, 2)
        self.alist.factory.undo()
        self.alist.factory.undo()
        self.assertEqual(self.set_calls_counter.count, 0)
        self.alist.factory.redo()
        self.alist.factory.redo()
        self.alist.factory.redo()
        self.assertEqual(self.set_calls_counter.count, 3)

    def test_setting_value_of_attribute_after_undoing_appending_it_to_the_list_does_not_run_set_method(self):
        new_attr = self.fac.new("integer")

        self.alist.append(new_attr)
        self.alist.factory.undo()

        new_attr.set(7)
        self.assertEqual(self.set_calls_counter.count, 0)

        #this redo is ignored as a new command (set) was run
        self.alist.factory.redo()
        new_attr.set(6)
        self.assertEqual(self.set_calls_counter.count, 0)

        # only after adding the 'new_attr' again to the list, the counter is again being updated
        self.alist.append(new_attr)
        self.set_calls_counter.count = 0
        new_attr.set(7)
        self.assertEqual(self.set_calls_counter.count, 1)

    def test_setting_value_of_removed_attribute_does_run_the_set_method_of_the_attribute_list_after_calling_the_undo(self):
        new_attr = self.fac.new("integer")
        self.alist.append(new_attr)
        self.alist.remove(new_attr)
        self.set_calls_counter.count = 0
        new_attr.set(5)
        self.assertEqual(self.set_calls_counter.count, 0)

        self.fac.undo() # undo setting the item's value to 5
        self.fac.undo() # undo removal
        self.set_calls_counter.count = 0
        self.assertTrue(new_attr in self.alist.attributes)
        new_attr.set(5)
        self.assertEqual(self.set_calls_counter.count, 1)

    def test_adding_attribute_calls_the_set_method(self):
        new_attr = self.fac.new("integer")
        self.set_calls_counter.count = 0
        self.alist.append(new_attr)
        self.assertEqual(self.set_calls_counter.count, 1)
        self.fac.undo()
        self.assertEqual(self.set_calls_counter.count, 0)
        self.fac.redo()
        self.assertEqual(self.set_calls_counter.count, 1)

    def test_removing_attribute_calls_the_set_method(self):
        new_attr = self.fac.new("integer")
        self.set_calls_counter.count = 0
        self.alist.append(new_attr)
        self.assertEqual(self.set_calls_counter.count, 1)
        self.alist.remove(new_attr)
        self.assertEqual(self.set_calls_counter.count, 2)



from typing import List
class Test_Calculating_Single_Attribute_From_Attribute_List(unittest.TestCase):

    def test_dot_product(self):
        fac = attribute_factory(Controller())
        dotprod = fac.new("integer")
        u = fac.newlist('integer', [2,0,3])
        v = fac.newlist('integer', [3,1,2])
        
        def calc_dotprod(u:list[int], v:list[int])->int:
            return sum([ui*vi for ui,vi in zip(u,v)])
        
        dotprod.add_dependency(calc_dotprod, u, v)
        self.assertEqual(dotprod.value, 12)

        u[0].set(0)
        self.assertEqual(dotprod.value, 6)

    def test_scaling_sum_of_list_of_integers(self):
        fac = attribute_factory(Controller())
        scaledsum = fac.new("real")
        scale = fac.new("real")
        scale.set(1.0)
        x = fac.newlist('real', [1.0 for _ in range(5)])

        def getsum(s:float, x:List[float])->float: return s*sum(x)

        scaledsum.add_dependency(getsum, scale, x)

        self.assertEqual(scaledsum.value, 5)
        scale.set(0.5)
        self.assertEqual(scaledsum.value, 2.5)
        fac.undo()
        self.assertEqual(scaledsum.value, 5)
        x.remove(x[-1])
        self.assertEqual(scaledsum.value, 4)

    def test_weighted_average(self):
        fac = attribute_factory(Controller())
        result = fac.new('real')
        weights = fac.newlist('real',[1,2])
        values = fac.newlist('real',[4,1])
        def w_average(values:List[float], weights:List[float])->float:
            return sum([v*w for v,w in zip(values,weights)])/sum(weights)
        
        result.add_dependency(w_average,values,weights)
        self.assertEqual(result.value,2)
        weights[-1].set(0)
        self.assertEqual(result.value,4)
        fac.undo()
        self.assertEqual(result.value,2)

    def test_undoing_increments_of_every_single_summand(self)->None:
        fac = attribute_factory(Controller())
        result = fac.new('integer', name='result')
        summands = fac.newlist('integer', [0,0,0], name='summands list')

        for k in range(len(summands.attributes)): summands[k].rename(f'summand {k}')
  
        def getsum(x:List[int])->int: return sum(x)
        result.add_dependency(getsum, summands)

        fac.controller.clear_history()
        for s in summands: s.set(1)   

        self.assertEqual(result.value, 3)
        fac.undo()

        self.assertEqual(result.value, 2)
        fac.undo()
        self.assertEqual(result.value, 1)
        fac.undo()
        self.assertEqual(result.value, 0)


    
    def test_undoing_setting_of_a_driving_attribute(self)->None:
        fac = attribute_factory(Controller())
        y = fac.new('integer', name='y')
        x = fac.new('integer', 0, name='x')

        def double(x:int)->int: return 2*x
        y.add_dependency(double, x)

        x.set(1)
        x.set(2)
        x.set(3)
        self.assertEqual(y.value, 6)
        fac.undo()
        self.assertEqual(y.value, 4)
        fac.undo()
        self.assertEqual(y.value, 2)
        fac.undo()
        self.assertEqual(y.value, 0)
        fac.undo()

        fac.redo()
        fac.redo()
        fac.redo()
        fac.redo()
        self.assertEqual(y.value, 6)


from typing import Tuple
class Test_Using_Attribute_List_As_Output(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())

    def foo(self,inputval:int)->List[int]:
        return [inputval for _ in range(3)]

    def test_copy_single_value_to_all_items_in_list(self):
        theinput = self.fac.new('integer',5)
        output = self.fac.newlist('integer', init_items=[0,0,0])

        output.add_dependency(self.foo, theinput)
        self.assertListEqual(output.value, [5,5,5])

        self.fac.undo()
        self.assertListEqual(output.value, [0,0,0])
        self.fac.redo()
        self.assertListEqual(output.value, [5,5,5])
        self.fac.undo()
        self.assertListEqual(output.value, [0,0,0])

        theinput.set(-1)
        self.assertListEqual(output.value, [-1,-1,-1])

        output.break_dependency()
        theinput.set(4)
        self.assertListEqual(output.value, [-1,-1,-1])

    def test_not_matching_types_of_output_values_and_attribute_list_type_raises_exception(self):
        theinput = self.fac.new('integer')
        output = self.fac.newlist('text', init_items=['abc','xyz', 'mno'])
        self.assertRaises(Attribute.InvalidValueType, output.add_dependency, self.foo, theinput)

    def test_adding_dependency_to_an_attribute_in_an_already_dependent_attribute_list_raises_exception(self):
        someinput = self.fac.new('integer')
        deplist = self.fac.newlist('integer', init_items=[0,1,2])
        deplist.add_dependency(self.foo, someinput)

        otherinput = self.fac.new('integer')
        def goo(x:int)->int: return x
        self.assertRaises(Attribute.DependencyAlreadyAssigned, deplist[0].add_dependency, goo, otherinput)
        # after breaking the dependency of the list, other dependency can be added to its items
        deplist.break_dependency()
        deplist[0].add_dependency(goo, otherinput)

    def test_attribute_list_containing_dependent_attributes_cannot_be_made_dependent(self):
        someinput = self.fac.new('integer')
        deplist = self.fac.newlist('integer', init_items=[0,1,2])

        otherinput = self.fac.new('integer')
        def goo(x:int)->int: return x
        deplist[0].add_dependency(goo, otherinput)
        self.assertRaises(Attribute_List.ItemIsAlreadyDependent, deplist.add_dependency, self.foo, someinput)

        # after releasing the item dependency, dependency can be added to the list
        deplist[0].break_dependency()
        deplist.add_dependency(self.foo, someinput)

    def test_cross_product(self):
        u = self.fac.newlist('real',[1,0,0])
        v = self.fac.newlist('real',[0,1,0])
        w = self.fac.newlist('real',[0,0,0])
        def cross(u:Tuple[int,int,int],v:Tuple[int,int,int])->Tuple[int,int,int]:
            return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        w.add_dependency(cross, u, v)
        self.assertEqual(cross((1,0,0), (0,1,0)), (0,0,1))

        self.assertListEqual(w.value, [0,0,1])
        u[0].set(2)
        self.assertListEqual(w.value, [0,0,2])

    def test_calculating_mass_fractions(self)->None:
        masses = self.fac.newlist('real',[3,5,2])
        fractions = self.fac.newlist('real',[0,0,0])
        def get_mass_fractions(masses:Tuple[float,...])->Tuple[float,...]:
            total_mass = sum(masses)
            if total_mass==0: 
                return tuple([0 for _ in masses])
            else: 
                return tuple([mi/total_mass for mi in masses])
            
        fractions.add_dependency(get_mass_fractions, masses)

        self.assertListEqual(fractions.value, [Decimal('0.3'), Decimal('0.5'), Decimal('0.2')])
        for attr in masses: attr.set(0)
        self.assertListEqual(fractions.value, [Decimal('0.0'), Decimal('0.0'), Decimal('0.0')])


class Test_Nested_Attribute_Lists(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())
        self.parent_list = self.fac.newlist('integer')

    def test_nested_attribute_list(self)->None:
        child_list = self.fac.newlist('integer', [1,2,4])
        self.parent_list.append(child_list)       
        self.assertEqual(self.parent_list[0].value[1], 2)

    def test_appending_list_to_itself_raises_exception(self):
        self.assertRaises(Attribute_List.ListContainsItself, self.parent_list.append, self.parent_list)

    def test_appending_parent_list_to_its_child_list_raises_exception(self):
        child_list = self.fac.newlist('integer')
        self.parent_list.append(child_list)   
        self.assertRaises(Attribute_List.ListContainsItself, child_list.append, self.parent_list)

    def test_outer_product(self):
        u = self.fac.newlist('integer', [1,-1])
        v = self.fac.newlist('integer', [2,3])
        def outer_product(u:Tuple[int,int],v:Tuple[int,int])->Tuple[Tuple[int,int], Tuple[int,int]]:
            return (
                (u[0]*v[0], u[0]*v[1]),
                (u[1]*v[0], u[1]*v[1])
            )
        prod = self.fac.newlist('integer')
        prod.append(self.fac.newlist('integer',[0,0]))
        prod.append(self.fac.newlist('integer',[0,0]))
        prod.add_dependency(outer_product, u, v)

        self.assertListEqual(prod.value, [
            [2, 3],
            [-2, -3]
        ])

        self.fac.undo()
        self.assertListEqual(prod.value, [
            [0, 0],
            [0, 0]
        ])


class Test_Copying_Attribute_List(unittest.TestCase):

    def setUp(self) -> None:
        self.fac = attribute_factory(Controller())
        self.alist = self.fac.newlist('integer', [1,2,3])

    def test_copying_attribute_list(self)->None:
        alistcopy = self.alist.copy()
        self.assertListEqual(alistcopy.value, [1,2,3])
        alistcopy[1].set(4)
        self.assertListEqual(self.alist.value, [1,2,3])
        self.assertListEqual(alistcopy.value, [1,4,3])

    def test_attribute_list_is_copied_without_dependency(self)->None:
        def copyval(x:int)->List[int]: return [x for _ in range(3)]
        x = self.fac.new('integer',1)
        self.alist.add_dependency(copyval, x)
        self.assertListEqual(self.alist.value, [1,1,1])
        alistcopy = self.alist.copy()
        self.assertListEqual(alistcopy.value, [1,1,1])
        x.set(2)
        self.assertListEqual(self.alist.value, [2,2,2])
        self.assertListEqual(alistcopy.value, [1,1,1])

    def test_list_copy_does_not_affect_an_attribute_that_depends_on_the_original_list(self):
        s = self.fac.new('integer', 2)
        s.add_dependency(sum, self.alist)
        self.assertEqual(s.value, 6)
        alistcopy = self.alist.copy()
        alistcopy._value_update([0,0,0])
        self.assertEqual(s.value, 6)



if __name__=="__main__": unittest.main()