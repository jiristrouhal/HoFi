import abc
from typing import List, Any


class Command(abc.ABC): # pragma: no cover
    def __init__(self, data:Any)->None: pass
    @abc.abstractmethod
    def run(self)->None: pass
    @abc.abstractmethod
    def undo(self)->None: pass
    @abc.abstractmethod
    def redo(self)->None: pass
    

class Controller:

    def __init__(self)->None:
        self.__undo_stack:List[List[Command]] = list()
        self.__redo_stack:List[List[Command]] = list()

    @property
    def any_undo(self)->bool: return bool(self.__undo_stack)
    @property
    def any_redo(self)->bool: return bool(self.__redo_stack)

    
    def run(self,*cmds:Command)->None:
        for cmd in cmds: cmd.run()
        self.__undo_stack.append(list(cmds))
        self.__redo_stack.clear()

    def undo(self)->None:
        if not self.__undo_stack: return 
        batch = self.__undo_stack.pop()    
        for cmd in reversed(batch): cmd.undo()
        self.__redo_stack.append(batch)

    def redo(self)->None:
        if not self.__redo_stack: return 
        batch = self.__redo_stack.pop()    
        for cmd in batch: cmd.redo()
        self.__undo_stack.append(batch)