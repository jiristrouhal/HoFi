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
    printops:Dict[str,Any] = {}

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

    def print(self, **options)->str:
        for op in options:
            if op not in self.printops: raise Attribute.UnknownOption
        return self._str_value(self._value,**options)
        
    @abc.abstractmethod
    def _str_value(cls, value:Any,**options)->str: # pragma: no cover
        pass

    def set(self,value:Any)->None: 
        if self._depends_on: return
        else: self._run_set_command(value)
    
    @abc.abstractmethod
    def is_valid(self, value:Any)->bool: pass # pragma: no cover

    @classmethod
    def _pick_format_option(cls,option,options:Dict[str,Any])->Any:
        if option in cls.printops:
            if option in options: return options[option]
            else: return cls.printops[option]
        else: raise Attribute.UnknownOption

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
        facs:List[Attribute_Factory] = list()
        cmds:List[List[Command]] = list()
        for attr,value in new_values.items():
            if attr._dependency is not None: continue #ignore dependent attributes
            if not attr._factory in facs: # Attribute_Factory is not hashable, two lists circumvent the problem
                facs.append(attr._factory)
                cmds.append(list())
            cmds[facs.index(attr._factory)].extend(attr.__get_set_command(value))
        
        for fac, cmd_list in zip(facs,cmds):
            fac.controller.run(*cmd_list)

    class CyclicDependency(Exception): pass
    class DependencyAlreadyAssigned(Exception): pass
    class GroupingAttributesFromDifferentFactories(Exception): pass
    class InvalidAttributeType(Exception): pass
    class InvalidDefaultValue(Exception): pass
    class InvalidValueType(Exception): pass
    class NoInputsForDependency(Exception): pass
    class UnknownOption(Exception): pass
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
        self.types['choice'] = Choice_Attribute
        self.types['date'] = Date_Attribute

    def new(self,atype:str='text',name:str="")->Attribute:
        if atype not in self.types: raise Attribute.InvalidAttributeType(atype)
        else:
            return self.types[atype](self,atype,name)
        
    def choice(self, name:str="")->Choice_Attribute:
        return Choice_Attribute(self,'choice',name)
        
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
    printopts:Dict[str,Any] = {}

    def is_valid(self, value:Any) -> bool:
        return isinstance(value,str)
    
    @classmethod
    def _str_value(cls, value:Any, **options:Any)->str:
        return str(value)


class Integer_Attribute(Attribute):
    default_value = 0
    printopts:Dict[str,Any] = {}

    def is_valid(self, value:Any) -> bool:
        try: 
            return int(value) is value
        except: 
            return False
    
    @classmethod
    def _str_value(cls, value:Any, **options) -> str:
        return str(value)
        
    
import math
class Real_Attribute(Attribute):
    default_value = 0
    printops:Dict[str,Any] = {'prec':30}

    def is_valid(self, value:Any) -> bool:
        try: 
            if math.isnan(value): return True
            float(value)==value
            return True
        except: 
            return False

    @classmethod
    def _str_value(cls, value, **options) -> str:
        precision = cls._pick_format_option('prec',options)
        return format(value, f'.{precision}f')
    

class Choice_Attribute(Attribute):
    default_value = ""
    printopts:Dict[str,Any] = {}

    def __init__(self, factory:Attribute_Factory, atype:str, name:str="")->None:
        self.options:List[Any] = list()
        super().__init__(factory, atype, name)

    @property
    def value(self)->Any: 
        if self.options: return self._value
        else: raise Choice_Attribute.OptionsNotDefined

    def add_options(self, *options:Any)->None:
        self.options.extend(options)

    def print_options(self, **format_options)->Tuple[str,...]:
        return tuple([self._str_value(op) for op in self.options])

    def remove_options(self,*options:Any)->None:
        if self._value in options: raise Choice_Attribute.CannotRemoveChosenOption
        for op in options:
            if op in self.options: 
                self.options.remove(op)
            else: 
                raise Choice_Attribute.NonexistentOption

    def set(self,value:Any)->None:
        if not self.options: raise Choice_Attribute.OptionsNotDefined
        super().set(value)

    def is_option(self, value:Any)->bool:
        return value in self.options

    def is_valid(self, value:Any) -> bool:
        if self.options and value not in self.options: 
            raise Choice_Attribute.NonexistentOption(value, f"available options: {self.options}")
        return True
    
    @classmethod
    def _str_value(cls, value, **format_options) -> str:
        return str(value)

    class CannotRemoveChosenOption(Exception): pass
    class NonexistentOption(Exception): pass
    class OptionsNotDefined(Exception): pass


import datetime
class Date_Attribute(Attribute):
    default_value = datetime.date.today()
    printops = {'local_code':'default'}
    __date_formats = {
        'cs_cz':'%d.%m.%y',
        'default':'%y-%m-%d'
    }

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, datetime.date)

    @classmethod
    def _str_value(cls, value: Any, **options) -> str:
        local_code = cls._pick_format_option('local_code',options)
        date_format = cls.__date_formats[local_code]
        return datetime.date.strftime(value,date_format)