from __future__ import annotations

from typing import Literal, Any, Callable
import typing
import abc
import dataclasses

from src.cmd.commands import Command, Composed_Command, Timing, Dict, Controller


@dataclasses.dataclass
class Set_Attr_Data:
    attr:Attribute
    value:Any
    def __post_init__(self)->None:
        if not self.attr.is_valid(self.value): raise Attribute.InvalidValueType

@dataclasses.dataclass
class Set_Attr(Command):
    data:Set_Attr_Data
    prev_value:Any = dataclasses.field(init=False)

    def run(self)->None:
        self.prev_value = self.data.attr.value
        self.data.attr._value = self.data.value
    def undo(self)->None:
        self.data.attr.set(self.prev_value)
    def redo(self)->None:
        self.data.attr.set(self.data.value)


class Set_Attr_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return Set_Attr

    def __call__(self, data:Set_Attr_Data):
        return super().__call__(data)
    
    def add(self, owner:str, func:Callable[[Set_Attr_Data],Command],timing:Timing)->None:
        super().add(owner,func,timing)
    


Attribute_Type = Literal['text','integer']
Command_Type = Literal['set']
class Attribute(abc.ABC):
    
    def __init__(self,controller:Controller,atype:Attribute_Type='text')->None:
        self.__type = atype
        self._value = ""
        self.command:Dict[Command_Type,Composed_Command] = {
            'set':Set_Attr_Composed()
        }
        self._controller = controller

    @property
    def type(self)->Attribute_Type: return self.__type
    @abc.abstractproperty
    def value(self)->Any: pass

    def on_set(self, owner:str, func:Callable[[Set_Attr_Data],Command], timing:Timing)->None: 
        self.command['set'].add(owner, func, timing)

    def set(self,value:Any)->None: 
        self._controller.run(self.command['set'](Set_Attr_Data(self,value)))

    def is_valid(self, value:Any)->bool: 
        if self.__type=='integer':
            try: 
                int(value+1)
                return True
            except: return False
        return True

    class DependencyNotSet(Exception): pass
    class InvalidAttributeType(Exception): pass
    class InvalidValueType(Exception): pass


class IndepAttribute(Attribute):
    @property
    def value(self)->Any: return self._value


class DependentAttribute(Attribute):
    def __init__(self,*args,**kwargs)->None:
        super().__init__(*args,**kwargs)
        self.dependency = None
    @property
    def value(self)->Any: 
        if self.dependency is None: raise Attribute.DependencyNotSet
        else: return ""

def new_attribute(controller:Controller, attr_type:Attribute_Type='text', dependent:bool=False)->Attribute:
    if attr_type not in typing.get_args(Attribute_Type): 
        raise Attribute.InvalidAttributeType(attr_type)

    if not dependent: return IndepAttribute(controller, attr_type)
    else: return DependentAttribute(controller, attr_type)




