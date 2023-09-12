from __future__ import annotations

import sys
sys.path.insert(1,"src")
import dataclasses
from typing import Protocol


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



from typing import Callable
class Composed_Increment(Composed_Command):
    @staticmethod
    def cmd_type(): return IncrementIntAttribute

    def execute(self, controller:Controller, data:IncrementIntData) -> None:
        super().execute(controller, data)

    def add(self,owner_id:str,func:Callable[[IncrementIntData],Command],timing:Timing)->None:
        super().add(owner_id,func,timing)



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

    def test_composed_command(self):
        obj = Integer_Owner(i=0)
        other_int = OtherInt()
        controller = Controller()

        composed_command = Composed_Increment()
        def get_cmd(data:IncrementIntData)->Increment_Other_Int:
            return Increment_Other_Int(other_int, data.obj)
        
        composed_command.add('test', get_cmd, 'post')
        composed_command.execute(controller,IncrementIntData(obj,step=5))
        self.assertEqual(obj.i, 5)
        self.assertEqual(other_int.value, 5)
        composed_command.execute(controller,IncrementIntData(obj,step=4))
        self.assertEqual(obj.i, 9)
        self.assertEqual(other_int.value, 9)
        controller.undo()
        self.assertEqual(obj.i, 5)
        self.assertEqual(other_int.value, 5)
        controller.redo()
        self.assertEqual(obj.i, 9)
        self.assertEqual(other_int.value, 9)
        controller.undo()
        self.assertEqual(obj.i, 5)
        self.assertEqual(other_int.value, 5)



if __name__=="__main__": unittest.main()