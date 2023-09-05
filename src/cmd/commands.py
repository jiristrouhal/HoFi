import abc
from typing import List


class Command(abc.ABC): # pragma: no cover
    @abc.abstractmethod
    def run(self)->None: pass
    @abc.abstractmethod
    def undo(self)->None: pass
    @abc.abstractmethod
    def redo(self)->None: pass
    

class Controller:

    def __init__(self)->None:
        self.__undo_stack:List[Command] = list()
        self.__redo_stack:List[Command] = list()

    @property
    def any_undo(self)->bool: return bool(self.__undo_stack)
    @property
    def any_redo(self)->bool: return bool(self.__redo_stack)

    
    def run(self,cmd:Command)->None:
        cmd.run()
        self.__undo_stack.append(cmd)
        self.__redo_stack.clear()

    def undo(self)->None:
        if not self.__undo_stack: return 
        cmd = self.__undo_stack.pop()    
        cmd.undo()
        self.__redo_stack.append(cmd)

    def redo(self)->None:
        if not self.__redo_stack: return 
        cmd = self.__redo_stack.pop()    
        cmd.redo()
        self.__undo_stack.append(cmd)