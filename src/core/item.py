from __future__ import annotations
from typing import Dict, Protocol, Any
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

    @property
    def name(self)->str: return self.__name
    @property
    def attributes(self)->Dict[str,Attribute]: 
        return self.__attributes.copy()
    @property
    def attribute_values(self)->Dict[str,Any]: 
        return {key:attr.value for key,attr in self.__attributes.items()}
    
    def rename(self,name:str)->None:
        self.__cmdcontroller.run(Rename(self,name))

    def undo(self)->None:
        self.__cmdcontroller.undo()

    def redo(self)->None:
        self.__cmdcontroller.redo()

    def _rename(self,name:str)->None:
        name = name.strip()
        self.__raise_if_name_is_blank(name)
        self.__name = name
    
    def __raise_if_name_is_blank(self,name:str)->None:
        if name=="": raise self.BlankName

    class BlankName(Exception): pass

