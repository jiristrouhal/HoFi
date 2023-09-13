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
    func:Callable[[Any],Any]
    attributes:Tuple[Attribute,...]
    old_value:Any = dataclasses.field(init=False)
    new_value:Any = dataclasses.field(init=False)
    def run(self)->None:
        self.old_value = self.attribute.value
        values = [a.value for a in self.attributes]
        self.attribute._run_set_command(self.func(*values))
        self.new_value = self.attribute.value
    def undo(self)->None:
        self.attribute._run_set_command(self.old_value)
    def redo(self)->None:
        self.attribute._run_set_command(self.new_value)



Command_Type = Literal['set']
from typing import Set
class Attribute(abc.ABC):

    default_value:Any = ""

    def __init__(self,controller:Controller,atype:str='text',name:str="")->None:
        self._name = name
        self._type = atype

        if self.is_valid(self.default_value): # pragma: no cover
            self._value = self.default_value # pragma: no cover
        else: # pragma: no cover
            raise Attribute.InvalidDefaultValue(
                f"Invalid default value ({self.default_value}) for attribute of type '{atype}'."
            ) # pragma: no cover

        self.command:Dict[Command_Type,Composed_Command] = {
            'set':Set_Attr_Composed()
        }
        self._controller = controller
        self._dependencies:Set[Attribute] = set()
        self._id = str(id(self))

    @property
    def type(self)->str: return self._type

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
    
    @abc.abstractmethod
    def is_valid(self, value:Any)->bool: pass # pragma: no cover
    
    def _check_for_dependency_cycle(self, attributes:Set[Attribute],path:str)->None:
        if self in attributes: 
            raise Attribute.CyclicDependency(path + ' -> ' + self._name)
        else:
            for attr in attributes:
                self._check_for_dependency_cycle(attr._dependencies,path + ' -> ' + attr._name)

    def add_dependency(self,dependency:Callable[[Any],Any], *attributes:Attribute)->None:
        self._check_for_dependency_cycle(set(attributes),path=self._name)
        this_id = str(id(self))
        def set_dependent_attr(data:Set_Attr_Data)->Any:
            return Set_Dependent_Attr(self,dependency,attributes)
        for attribute in attributes:
            attribute.on_set(this_id, set_dependent_attr, 'post')
            self._dependencies.add(attribute)

    def remove_dependencies(self)->None:
        for attribute_affecting_this_one in self._dependencies: 
            attribute_affecting_this_one.command['set'].post.pop(self._id)
        self._dependencies.clear()
        
    class CyclicDependency(Exception): pass
    class InvalidAttributeType(Exception): pass
    class InvalidDefaultValue(Exception): pass
    class InvalidValueType(Exception): pass


from typing import Type
@dataclasses.dataclass
class Attribute_Factory:
    controller:Controller
    types:Dict[str,Type[Attribute]] = dataclasses.field(default_factory=dict)
    def __post_init__(self)->None:
        self.types['text'] = Text_Attribute
        self.types['integer'] = Integer_Attribute

    def new(self,atype:str='text',name:str="")->Attribute:
        if atype not in self.types: raise Attribute.InvalidAttributeType(atype)
        else:
            return self.types[atype](self.controller,atype,name)


def attribute_factory(controller:Controller)->Attribute_Factory:
    return Attribute_Factory(controller)



class Text_Attribute(Attribute):
    default_value = ""

    def is_valid(self, value:Any) -> bool:
        return isinstance(value,str)


class Integer_Attribute(Attribute):
    default_value = 0

    def is_valid(self, value:Any) -> bool:
        try: 
            int(value+1)
            return True
        except: 
            return False


