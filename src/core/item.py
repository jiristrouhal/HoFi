from __future__ import annotations
from typing import Dict, Protocol, Any, Set
import dataclasses
from src.cmd.commands import Command, Controller



class Attribute(Protocol): # pragma: no cover

    @property
    def value(self)->Any: ...


@dataclasses.dataclass
class Rename(Command):
    item:Item
    new_name:str
    original_name:str = dataclasses.field(init=False)

    def run(self):
        self.original_name = self.item.name
        self.item._rename(self.new_name)

    def undo(self):
        self.item._rename(self.original_name)
    
    def redo(self) -> None:
        self.item._rename(self.new_name)


class Item:
    
    def __init__(self,name:str,attributes:Dict[str,Attribute]={})->None:
        self.__cmdcontroller = Controller()
        self.__attributes = attributes
        self._rename(name)
        self.__children:Set[Item] = set()
        self.__parent:Item|None = None

    @property
    def attributes(self)->Dict[str,Attribute]: 
        return self.__attributes.copy()
    
    @property
    def attribute_values(self)->Dict[str,Any]: 
        return {key:attr.value for key,attr in self.__attributes.items()}
    
    @property
    def name(self)->str: return self.__name

    @property
    def parent(self)->Item|None: return self.__parent

    def _adopt_by(self,item:Item)->None:
        if self.parent is None: self.__parent=item
    
    def adopt(self, child:Item)->None:
        child._adopt_by(self)
        if self is child.parent:
            self.__children.add(child)

    def pass_to_new_parent(self, child:Item, new_parent:Item)->None:
        child.leave_parent(self)
        new_parent.adopt(child)

    def is_child(self, child:Item)->bool: 
        return child in self.__children
    
    def leave_child(self,child:Item)->None:
        if child in self.__children:
            self.__children.remove(child)
            child.leave_parent(self)
    
    def leave_parent(self,parent:Item)->None:
        if parent is self.parent:
            self.__parent.leave_child(self)
            self.__parent = None

    def redo(self)->None:
        self.__cmdcontroller.redo()

    def rename(self,name:str)->None:
        self.__cmdcontroller.run(Rename(self,name))

    def undo(self)->None:
        self.__cmdcontroller.undo()

    def _rename(self,name:str)->None:
        name = name.strip()
        self.__raise_if_name_is_blank(name)
        self.__name = name
    
    def __raise_if_name_is_blank(self,name:str)->None:
        if name=="": raise self.BlankName

    class BlankName(Exception): pass

