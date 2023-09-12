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

@dataclasses.dataclass
class Set_Attr(Command):
    data:Set_Attr_Data
    prev_value:Any = dataclasses.field(init=False)

    def run(self)->None:
        self.prev_value = self.data.attr.value
        self.data.attr._check_and_set_value(self.data.value)
    def undo(self)->None:
        self.data.attr._check_and_set_value(self.prev_value)
    def redo(self)->None:
        self.data.attr._check_and_set_value(self.data.value)


class Set_Attr_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return Set_Attr

    def __call__(self, data:Set_Attr_Data):
        return super().__call__(data)
    
    def add(self, owner:str, func:Callable[[Set_Attr_Data],Command],timing:Timing)->None:
        super().add(owner,func,timing)


from typing import Tuple
@dataclasses.dataclass
class Set_Dependent_Attr(Command):
    attribute:Attribute
    func:Callable[[Attribute],Any]
    attributes:Tuple[Attribute,...]
    old_value:Any = dataclasses.field(init=False)
    new_value:Any = dataclasses.field(init=False)
    def run(self)->None:
        self.old_value = self.attribute.value
        self.attribute._run_set_command(self.func(*self.attributes))
        self.new_value = self.attribute.value
    def undo(self)->None:
        self.attribute._run_set_command(self.old_value)
    def redo(self)->None:
        self.attribute._run_set_command(self.new_value)


Attribute_Type = Literal['text','integer']
Command_Type = Literal['set']
from typing import Set, List
class Attribute(abc.ABC):
    
    def __init__(self,controller:Controller,atype:Attribute_Type='text',name:str="")->None:
        self._name = name
        self._type = atype
        self._value = ""
        self.command:Dict[Command_Type,Composed_Command] = {
            'set':Set_Attr_Composed()
        }
        self._controller = controller
        self._dependencies:Set[Attribute] = set()
        self._id = str(id(self))

    @property
    def type(self)->Attribute_Type: return self._type

    @property
    def value(self)->Any: return self._value

    def on_set(self, owner:str, func:Callable[[Set_Attr_Data],Command], timing:Timing)->None: 
        self.command['set'].add(owner, func, timing)

    def set(self,value:Any)->None: 
        if self._dependencies: 
            return
        else:
            self._run_set_command(value)

    def _run_set_command(self,value:Any)->None:
        self._controller.run(self.command['set'](Set_Attr_Data(self,value)))

    def _check_and_set_value(self,value:Any)->None:
        if not self.is_valid(value): raise Attribute.InvalidValueType
        else: self._value = value
    
    def is_valid(self, value:Any)->bool: 
        if self._type=='integer':
            try: 
                int(value+1)
                return True
            except: return False
        return True
    
    def _check_for_dependency_cycle(self, attributes:Set[Attribute],path:str)->None:
        if self in attributes: 
            raise Attribute.CyclicDependency(path + ' -> ' + self._name)
        else:
            for attr in attributes:
                self._check_for_dependency_cycle(attr._dependencies,path + ' -> ' + attr._name)

    def add_dependency(self,dependency:Callable[[Attribute],Any], *attributes:Attribute)->None:

        self._check_for_dependency_cycle(set(attributes),path=self._name)
        
        this_id = str(id(self))

        def set_dependent_attr(data:Set_Attr_Data)->Any:
            return Set_Dependent_Attr(self,dependency,attributes)

        for attribute in attributes:
            attribute.on_set(this_id, set_dependent_attr, 'post')
            self._dependencies.add(attribute)

    def remove_dependency(self)->None:
        for attribute_affecting_this_one in self._dependencies: 
            attribute_affecting_this_one.command['set'].post.pop(self._id)
        self._dependencies.clear()
        
    class CyclicDependency(Exception): pass
    class InvalidAttributeType(Exception): pass
    class InvalidValueType(Exception): pass



def new_attribute(controller:Controller, attr_type:Attribute_Type='text',name:str="")->Attribute:
    if attr_type not in typing.get_args(Attribute_Type): 
        raise Attribute.InvalidAttributeType(attr_type)

    return Attribute(controller, attr_type, name)




