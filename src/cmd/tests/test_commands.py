import sys
sys.path.insert(1,"src")
import dataclasses


import unittest
from src.cmd.commands import Controller, Command


@dataclasses.dataclass
class Integer_Owner:
    i:int


@dataclasses.dataclass
class IncrementIntAttribute(Command):
    obj:Integer_Owner
    step:int=1
    def run(self)->None: self.obj.i += self.step
    def undo(self)->None: self.obj.i -= self.step
    def redo(self)->None: self.obj.i += self.step


class Test_Running_A_Command(unittest.TestCase):

    def setUp(self) -> None:
        self.obj = Integer_Owner(i=5)
        self.controller = Controller()

    def test_single_undo_returns_the_object_state_back_to_previous_state(self):
        self.controller.run(IncrementIntAttribute(self.obj))
        self.assertEqual(self.obj.i, 6)
        self.controller.undo()
        self.assertEqual(self.obj.i, 5)

    def test_single_undo_and_single_redo_returns_the_object_to_state_after_first_run(self):
        self.controller.run(IncrementIntAttribute(self.obj))
        self.controller.undo()
        self.controller.redo()
        self.assertEqual(self.obj.i, 6)

    def test_second_undo_does_nothing_after_a_single_command_run(self):
        self.controller.run(IncrementIntAttribute(self.obj))        
        self.controller.undo()
        self.controller.undo()
        self.assertEqual(self.obj.i, 5)

    def test_after_executing_new_command_redo_has_no_effect(self):
        self.controller.run(IncrementIntAttribute(self.obj, step=5))
        self.controller.undo()
        self.controller.run(IncrementIntAttribute(self.obj, step=7))
        self.assertEqual(self.obj.i, 12)
        self.controller.redo()
        self.assertEqual(self.obj.i, 12)

    def test_examining_if_there_are_undos_available(self):
        self.assertFalse(self.controller.any_undo)
        self.controller.run(IncrementIntAttribute(self.obj))
        self.assertTrue(self.controller.any_undo)
        self.controller.undo()
        self.assertFalse(self.controller.any_undo)

    def test_examining_if_there_are_redos_available(self):
        self.assertFalse(self.controller.any_redo)
        self.controller.run(IncrementIntAttribute(self.obj))
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
            IncrementIntAttribute(obj, 2),
            MultiplyIntAttribute(obj, 3)
        )
        self.assertEqual(obj.i, 6)

        controller.undo()
        self.assertEqual(obj.i, 0)
        controller.redo()
        self.assertEqual(obj.i, 6)
        controller.undo()
        self.assertEqual(obj.i, 0)


if __name__=='__main__': unittest.main()