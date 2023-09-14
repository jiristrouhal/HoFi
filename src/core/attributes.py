from __future__ import annotations

from typing import Literal, Any, Callable
import abc
import dataclasses

from src.cmd.commands import Command, Composed_Command, Timing, Dict, Controller


@dataclasses.dataclass
class Dependency:
    func:Callable[[Any],Any]
    
    def __call__(self,*values)->Any: 
        try:
            result = self.func(*values)
            return result
        except ValueError:
            return float('nan')
        except ZeroDivisionError:
            return float('nan')
        except TypeError:
            raise self.InvalidArgumentType
        except: # pragma: no cover
            return None # pragma: no cover
        
    class InvalidArgumentType(Exception): pass

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
    func:Callable[[Any],Any]|Dependency
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
from typing import Set, List
class Attribute(abc.ABC):
    default_value:Any = ""

    def __init__(self,factory:Attribute_Factory, atype:str='text',name:str="")->None:
        self._name = name
        self._type = atype
        self.command:Dict[Command_Type,Composed_Command] = {'set':Set_Attr_Composed()}
        self._depends_on:Set[Attribute] = set()
        self._dependency:Callable[[Any],Any]|Dependency|None = None
        self._id = str(id(self))
        self.__set_to_default_value()
        self._factory = factory

    @property
    def type(self)->str: return self._type
    @property 
    def value(self)->Any: return self._value
    
    def add_dependency(self,dependency:Callable[[Any],Any]|Dependency, *attributes:Attribute)->None:
        self.__check_dependency_has_at_least_one_input(attributes)
        self.__check_attribute_types_for_dependency(dependency, attributes)
        self.__check_for_existing_dependency()
        self.__check_for_dependency_cycle(set(attributes),path=self._name)

        command = Set_Dependent_Attr(self,dependency,attributes)
        command.run()

        def set_dependent_attr(data:Set_Attr_Data)->Any:
            return Set_Dependent_Attr(self,dependency,attributes)
        
        for attribute in attributes:
            attribute.on_set(self._id, set_dependent_attr, 'post')
            self._depends_on.add(attribute)
        self._dependency = dependency

    def break_dependency(self)->None:
        for attribute_affecting_this_one in self._depends_on: 
            attribute_affecting_this_one.command['set'].post.pop(self._id)
        self._depends_on.clear()
        self._dependency = None

    def copy(self)->Attribute:
        the_copy = self._factory.new(self._type, self._name)
        self.__set_value_of_the_copy(the_copy)
        return the_copy

    def on_set(self, owner:str, func:Callable[[Set_Attr_Data],Command], timing:Timing)->None: 
        self.command['set'].add(owner, func, timing)

    def set(self,value:Any)->None: 
        if self._depends_on: return
        else: self._run_set_command(value)
    
    @abc.abstractmethod
    def is_valid(self, value:Any)->bool: pass # pragma: no cover

    def _run_set_command(self,value:Any)->None:
        self._factory.controller.run(self.__get_set_command(value))

    def __get_set_command(self,value:Any)->Tuple[Command,...]:
        return self.command['set'](Set_Attr_Data(self,value))

    def _check_and_set_value(self,value:Any)->None:
        if not self.is_valid(value): raise Attribute.InvalidValueType
        else: self._value = value

    def __check_dependency_has_at_least_one_input(self,inputs:Tuple[Attribute,...])->None:
        if not inputs: raise Attribute.NoInputsForDependency

    def __check_for_dependency_cycle(self, attributes:Set[Attribute],path:str)->None:
        if self in attributes: raise Attribute.CyclicDependency(path + ' -> ' + self._name)
        else:
            for attr in attributes:
                self.__check_for_dependency_cycle(attr._depends_on,path + ' -> ' + attr._name)

    def __check_for_existing_dependency(self)->None:
        if self._depends_on: raise Attribute.DependencyAlreadyAssigned
        
    def __check_attribute_types_for_dependency(
        self,
        dependency:Callable[[Any],Any]|Dependency,
        attributes:Tuple[Attribute,...]
        )->None:

        values = [a.value for a in attributes]
        result = None
        try:
            result = dependency(*values)
        except TypeError:
            raise Attribute.WrongAttributeTypeForDependencyInput
        except Dependency.InvalidArgumentType:
            raise Attribute.WrongAttributeTypeForDependencyInput

        if not self.is_valid(result):
            raise Attribute.WrongAttributeTypeForDependencyOutput(result)
        
    def __set_to_default_value(self)->None:
        if self.is_valid(self.default_value): # pragma: no cover
            self._value = self.default_value # pragma: no cover
        else: # pragma: no cover
            raise Attribute.InvalidDefaultValue(
                f"Invalid default value ({self.default_value}) for attribute of type '{self.type}'."
            ) # pragma: no cover
        
    def __set_value_of_the_copy(self,the_copy:Attribute)->None:
        if self._dependency is not None:
            the_copy.add_dependency(self._dependency, *self._depends_on)
        else:
            the_copy._value = self._value

    @staticmethod
    def set_multiple(new_values:Dict[Attribute,Any])->None:
        fac = Attribute.__single_common_factory(list(new_values.keys()))

        cmds:List[Command] = list()
        for attr,value in new_values.items():
            if attr._dependency is not None: continue #ignore dependent attributes
            cmds.extend(attr.__get_set_command(value))
        fac.controller.run(*cmds)
        
    @staticmethod
    def __single_common_factory(attributes:List[Attribute])->Attribute_Factory:
        if not attributes: raise Attribute.NoAttributesProvided
        fac = attributes[-1]._factory
        for a in attributes[:-1]:
            if a._factory is not fac: 
                raise Attribute.GroupingAttributesFromDifferentFactories
        return fac

    class CyclicDependency(Exception): pass
    class DependencyAlreadyAssigned(Exception): pass
    class NoAttributesProvided(Exception): pass
    class GroupingAttributesFromDifferentFactories(Exception): pass
    class InvalidAttributeType(Exception): pass
    class InvalidDefaultValue(Exception): pass
    class InvalidValueType(Exception): pass
    class NoInputsForDependency(Exception): pass
    class WrongAttributeTypeForDependencyInput(Exception): pass
    class WrongAttributeTypeForDependencyOutput(Exception): pass


from typing import Type
@dataclasses.dataclass
class Attribute_Factory:
    controller:Controller
    types:Dict[str,Type[Attribute]] = dataclasses.field(default_factory=dict,init=False)
    def __post_init__(self)->None:
        self.types['text'] = Text_Attribute
        self.types['integer'] = Integer_Attribute
        self.types['real'] = Real_Attribute

    def new(self,atype:str='text',name:str="")->Attribute:
        if atype not in self.types: raise Attribute.InvalidAttributeType(atype)
        else:
            return self.types[atype](self,atype,name)
        
    def add(self,label:str,new_attribute_class:Type[Attribute])->None:
        if label in self.types:
            raise Attribute_Factory.TypeAlreadyDefined(
                f"Label '{label}' already assigned to attribute class '{self.types[label]}'."
            )
        else:
            self.types[label] = new_attribute_class

    class TypeAlreadyDefined(Exception): pass


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
            return int(value) is value
        except: 
            return False
        
    
import math
class Real_Attribute(Attribute):
    default_value = 0

    def is_valid(self, value:Any) -> bool:
        try: 
            if math.isnan(value): return True
            float(value)==value
            return True
        except: 
            return False


