from __future__ import annotations

import sys
sys.path.insert(1,"src")
import dataclasses


import unittest
from src.cmd.commands import Controller, Command


@dataclasses.dataclass
class Integer_Owner:
    i:int


@dataclasses.dataclass
class IncrementIntData:
    obj:Integer_Owner
    step:int=1

@dataclasses.dataclass
class IncrementIntAttribute(Command):
    data:IncrementIntData
    def run(self)->None: 
        self.data.obj.i += self.data.step
    def undo(self)->None: 
        self.data.obj.i -= self.data.step
    def redo(self)->None: 
        self.data.obj.i += self.data.step


class Test_Running_A_Command(unittest.TestCase):

    def setUp(self) -> None:
        self.obj = Integer_Owner(i=5)
        self.controller = Controller()

    def test_single_undo_returns_the_object_state_back_to_previous_state(self):
        self.controller.run(IncrementIntAttribute(IncrementIntData(self.obj)))
        self.assertEqual(self.obj.i, 6)
        self.controller.undo()
        self.assertEqual(self.obj.i, 5)

    def test_single_undo_and_single_redo_returns_the_object_to_state_after_first_run(self):
        self.controller.run(IncrementIntAttribute(IncrementIntData(self.obj)))
        self.controller.undo()
        self.controller.redo()
        self.assertEqual(self.obj.i, 6)

    def test_second_undo_does_nothing_after_a_single_command_run(self):
        self.controller.run(IncrementIntAttribute(IncrementIntData(self.obj)))        
        self.controller.undo()
        self.controller.undo()
        self.assertEqual(self.obj.i, 5)

    def test_after_executing_new_command_redo_has_no_effect(self):
        self.controller.run(IncrementIntAttribute(IncrementIntData(self.obj, step=5)))
        self.controller.undo()
        self.controller.run(IncrementIntAttribute(IncrementIntData(self.obj, step=7)))
        self.assertEqual(self.obj.i, 12)
        self.controller.redo()
        self.assertEqual(self.obj.i, 12)

    def test_examining_if_there_are_undos_available(self):
        self.assertFalse(self.controller.any_undo)
        self.controller.run(IncrementIntAttribute(IncrementIntData(self.obj)))
        self.assertTrue(self.controller.any_undo)
        self.controller.undo()
        self.assertFalse(self.controller.any_undo)

    def test_examining_if_there_are_redos_available(self):
        self.assertFalse(self.controller.any_redo)
        self.controller.run(IncrementIntAttribute(IncrementIntData(self.obj)))
        self.assertFalse(self.controller.any_redo)
        self.controller.undo()
        self.assertTrue(self.controller.any_redo)



@dataclasses.dataclass
class MultiplyIntAttribute(Command):
    obj:Integer_Owner
    factor:int
    prev_value:int = dataclasses.field(init=False)
    new_value:int = dataclasses.field(init=False)

    def run(self)->None: 
        self.prev_value = self.obj.i
        self.obj.i *= self.factor
        self.new_value = self.obj.i

    def undo(self)->None: 
        self.obj.i = self.prev_value

    def redo(self)->None: 
        self.obj.i = self.new_value


class Test_Running_Multiple_Commands(unittest.TestCase):

    def test_undo_and_redo_two_commands_at_once(self)->None:
        obj = Integer_Owner(0)
        controller = Controller()
        controller.run(
            IncrementIntAttribute(IncrementIntData(obj, 2)),
            MultiplyIntAttribute(obj, 3)
        )
        self.assertEqual(obj.i, 6)

        controller.undo()
        self.assertEqual(obj.i, 0)
        controller.redo()
        self.assertEqual(obj.i, 6)
        controller.undo()
        self.assertEqual(obj.i, 0)


from src.cmd.commands import Composed_Command, Timing
@dataclasses.dataclass
class OtherInt:
    value:int = 0



from typing import Any, Callable
class Composed_Increment(Composed_Command):
    @staticmethod
    def cmd_type(): return IncrementIntAttribute

    def __call__(self, data:IncrementIntData):
        return super().__call__(data)

    def add(self,owner_id:str,func:Callable[[IncrementIntData],Command],timing:Timing)->None:
        super().add(owner_id,func,timing)

    def add_composed(self, owner_id: str, data_converter: Callable[[IncrementIntData], Any], cmd: Composed_Command, timing: Timing) -> None:
        return super().add_composed(owner_id, data_converter, cmd, timing)


@dataclasses.dataclass
class Increment_Other_Int(Command):
    other_int:OtherInt
    obj:Integer_Owner
    prev_value:int = dataclasses.field(init=False)
    curr_value:int = dataclasses.field(init=False)

    def run(self) -> None:
        self.prev_value = self.other_int.value
        self.other_int.value = self.obj.i
        self.curr_value = self.other_int.value
    def undo(self)->None:
        self.other_int.value = self.prev_value
    def redo(self)->None:
        self.other_int.value = self.curr_value


class Test_Composed_Command(unittest.TestCase):

    def setUp(self) -> None:
        self.obj = Integer_Owner(i=0)
        self.other_int = OtherInt()
        self.controller = Controller()

    def get_cmd(self,data:IncrementIntData)->Increment_Other_Int:
        return Increment_Other_Int(self.other_int, data.obj)
    
    def test_composed_command(self):
        composed_command = Composed_Increment()
        
        composed_command.add('test', self.get_cmd, 'post')
        self.controller.run(*composed_command(IncrementIntData(self.obj,step=5)))
        self.assertEqual(self.obj.i, 5)
        self.assertEqual(self.other_int.value, 5)
        self.controller.run(*composed_command(IncrementIntData(self.obj,step=4)))
        self.assertEqual(self.obj.i, 9)
        self.assertEqual(self.other_int.value, 9)
        self.controller.undo()
        self.assertEqual(self.obj.i, 5)
        self.assertEqual(self.other_int.value, 5)
        self.controller.redo()
        self.assertEqual(self.obj.i, 9)
        self.assertEqual(self.other_int.value, 9)
        self.controller.undo()
        self.assertEqual(self.obj.i, 5)
        self.assertEqual(self.other_int.value, 5)

    def test_adding_command_under_invalid_timing_key(self):
        composed_command = Composed_Increment()
        self.assertRaises(KeyError, composed_command.add, 'test', self.get_cmd, 'invalid key')

    def test_adding_composed_command_to_composed_command(self):
        composed_command_pre = Composed_Increment()
        composed_command = Composed_Increment()
        composed_command_post = Composed_Increment()

        composed_command_post.add('test', self.get_cmd, 'post')
        def data_converter(input_data:IncrementIntData)->IncrementIntData:
            return input_data
        
        # each composed command should increment the integer by 5

        #the composed_command_pre adds the first 5 to the integer
        composed_command.add_composed('test', data_converter, composed_command_pre, 'pre')
        # the post-command of the composed_command follows, adding another 5

        # at last, the composed_command_post adds 5, which yields 15 in total
        composed_command.add_composed('test', data_converter, composed_command_post, 'post')

        # the increment is set the same for all three composed commands
        self.controller.run(*composed_command(IncrementIntData(self.obj, step=5)))
        self.assertEqual(self.obj.i, 15)

        # after resetting the integer to zero, is is possible to set up the data converter
        # such that the increment for the pre and post composed_command differs from the
        # origina increment

        self.obj.i = 0
        def data_converter(input_data:IncrementIntData)->IncrementIntData:
            return IncrementIntData(input_data.obj, step=2)
        
            # return IncrementIntData(input_data)
        # replaces the original pre- composed_command 
        composed_command.add_composed('test', data_converter, composed_command_pre, 'pre')
        composed_command.add_composed('test', data_converter, composed_command_post, 'post')
        self.controller.run(*composed_command(IncrementIntData(self.obj, step=5)))
        self.assertEqual(self.obj.i, 9)


if __name__=="__main__": unittest.main()