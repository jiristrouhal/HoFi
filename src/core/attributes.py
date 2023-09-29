from __future__ import annotations

from typing import Literal, Any, Callable, get_args, Tuple, Dict
import abc
import dataclasses

from src.cmd.commands import Command, Composed_Command, Timing, Controller


NBSP = u"\u00A0"


from decimal import Decimal, getcontext
getcontext().prec = 28
Locale_Code = Literal['cs_cz','en_us']
class UnknownLocaleCode(Exception): pass
def verify_and_format_locale_code(locale_code:Locale_Code)->str:
    if not locale_code.lower() in get_args(Locale_Code): raise UnknownLocaleCode(locale_code)
    code = locale_code.lower()
    return code


class Dependency(abc.ABC):

    def __init__(self, output:AbstractAttribute, func:Callable[[Any],Any], *inputs:AbstractAttribute):
        self._output = output
        self.func = func
        if not inputs: raise Dependency.NoInputs
        self.inputs = list(inputs)
        if self._output.dependent: raise Attribute.DependencyAlreadyAssigned 
        self.__check_input_types()
        self._check_for_dependency_cycle(self._output, path=self._output.name)
        self.__set_up_command(*self.inputs)

    @abc.abstractmethod
    def release(self)->None: pass  # pragma: no cover
    @property
    def output(self)->AbstractAttribute: return self._output
        
    def __check_input_types(self)->None:
        values = self.collect_input_values()
        try:
            result = self(*values)
            self._output.is_valid(result)
        except Dependency.InvalidArgumentType:
            raise Dependency.WrongAttributeTypeForDependencyInput([type(v) for v in values])
        
    def collect_input_values(self)->List[Any]:
        return [item.value for item in self.inputs]

    def _check_for_dependency_cycle(self, output:AbstractAttribute, path:str)->None:
        if output in self.inputs: 
            raise Dependency.CyclicDependency(path + ' -> ' + output.name)  
        for input in self.inputs:
            if not input.dependent: continue
            input.dependency._check_for_dependency_cycle(output, path + ' -> ' + input.name)
        
    def _add_set_up_command_to_input(self, *inputs:AbstractAttribute)->None:
        for input in inputs:
            input.command['set'].add_composed(
                self._output.id, 
                self._data_converter,
                self._output.command['set'], 
                'post'
        )
            
    def _data_converter(self,*args)->Set_Attr_Data:
        value_getter = lambda: self(*self.collect_input_values())
        return Set_Attr_Data(self._output, value_getter)
        
    def _set_output_value(self,*args)->Command: 
        return Set_Attr(self._data_converter(*args))
        
    def __set_up_command(self,*inputs:AbstractAttribute):
        self._output.factory.run(self._set_output_value())
        self._add_set_up_command_to_input(*inputs)

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
        
    class CyclicDependency(Exception): pass
    class InputAlreadyUsed(Exception): pass
    class InvalidArgumentType(Exception): pass
    class NoInputs(Exception): pass
    class NonexistentInput(Exception): pass
    class WrongAttributeTypeForDependencyInput(Exception): pass


class DependencyImpl(Dependency):
    class NullDependency(Dependency):  # pragma: no cover
        def __init__(self)->None:  
            self.func:Callable = lambda x: None  
            self.attributes:List[AbstractAttribute] = list()
        def release(self)->None: pass  

    NULL = NullDependency()

    def release(self)->None:
        for input in self.inputs: 
            input.command['set'].composed_post.pop(self.output.id)
            self.inputs.remove(input)
        self.output._forget_dependency()


@dataclasses.dataclass
class Set_Attr_Data:
    attr:AbstractAttribute
    value:Callable[[],Any]


@dataclasses.dataclass
class Set_Attr(Command):
    data:Set_Attr_Data
    old_value:Any = dataclasses.field(init=False)
    new_value:Any = dataclasses.field(init=False)
    @property
    def message(self)->str: 
        return f"Set Attribute | {self.data.attr.name}: Set to {self.new_value}"

    def run(self)->None:
        self.old_value = self.data.attr.value
        values = self.data.value()
        self.data.attr._value_update(values)
        self.new_value = self.data.attr.value
    def undo(self)->None:
        self.data.attr._value_update(self.old_value)
    def redo(self)->None:
        self.data.attr._value_update(self.new_value)


class Set_Attr_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return Set_Attr

    def __call__(self, data:Set_Attr_Data):
        return super().__call__(data)
    
    def add(self, owner:str, func:Callable[[Set_Attr_Data],Command],timing:Timing)->None:
        super().add(owner,func,timing)

    def add_composed(self, owner_id: str, data_converter: Callable[[Set_Attr_Data], Any], cmd: Composed_Command, timing: Timing) -> None:
        return super().add_composed(owner_id, data_converter, cmd, timing)

@dataclasses.dataclass
class Edit_AttrList_Data:
    alist:Attribute_List
    attribute:AbstractAttribute

@dataclasses.dataclass
class Append_To_Attribute_List(Command):
    data:Edit_AttrList_Data
    composed_post_set:Tuple[Callable, Composed_Command] = dataclasses.field(init=False)

    @property
    def message(self)->str: 
        return f"Append attribute to list | Attribute '{self.data.attribute.name}' appended to '{self.data.alist.name}'."

    def run(self)->None:
        self.data.alist._add(self.data.attribute)
        def get_list_set_data(data:Set_Attr_Data)->Set_Attr_Data:
            value_getter = lambda: self.data.alist.value + [data.value()]
            return Set_Attr_Data(
                self.data.alist, 
                value_getter
            )
        self.data.attribute.command['set'].add_composed(
            owner_id = self.data.alist.id,
            data_converter = get_list_set_data,
            cmd = self.data.alist.command['set'],
            timing = 'post'
        )

    def undo(self)->None:
        self.data.alist._remove(self.data.attribute)
        self.composed_post_set = self.data.attribute.command['set'].composed_post.pop(self.data.alist.id)

    def redo(self)->None:
        self.data.alist._add(self.data.attribute)
        self.data.attribute.command['set'].composed_post[self.data.alist.id] = self.composed_post_set

@dataclasses.dataclass
class Remove_From_Attribute_List(Command):
    data:Edit_AttrList_Data
    composed_post_set:Tuple[Callable, Composed_Command] = dataclasses.field(init=False)

    def run(self)->None:
        self.data.alist._remove(self.data.attribute)
        self.composed_post_set = self.data.attribute.command['set'].composed_post.pop(self.data.alist.id)
    def undo(self)->None:
        self.data.alist._add(self.data.attribute)
        self.data.attribute.command['set'].composed_post[self.data.alist.id] = self.composed_post_set
    def redo(self)->None:
        self.data.alist._remove(self.data.attribute)
        self.composed_post_set = self.data.attribute.command['set'].composed_post.pop(self.data.alist.id)

    @property
    def message(self)->str:
        return f"Remove attribute from list | Attribute '{self.data.attribute.name}' removed from '{self.data.alist.name}'."

class AbstractAttribute(abc.ABC):
    NullDependency = DependencyImpl.NULL

    def __init__(self, factory:Attribute_Factory, atype:str, name:str="")->None:
        if not isinstance(name,str): 
            raise AbstractAttribute.Invalid_Name
        self.__name = name
        self.__type = atype
        self.command:Dict[Command_Type,Composed_Command] = {'set':Set_Attr_Composed()}
        self.__id = str(id(self))
        self.__factory = factory
        self._dependency:Dependency = DependencyImpl.NULL

    @property
    def name(self)->str: return self.__name
    @abc.abstractproperty
    def value(self)->Any: pass   # pragma: no cover
    @property
    def factory(self)->Attribute_Factory: return self.__factory
    @property
    def id(self)->str: return self.__id
    @property
    def type(self)->str: return self.__type

    @property
    def dependency(self)->Dependency: return self._dependency
    @property 
    def dependent(self)->bool:
        return self._dependency is not Attribute.NullDependency
    
    def add_dependency(self,func:Callable[[Any],Any], *attributes:AbstractAttribute)->None:
        self._dependency = DependencyImpl(self, func, *attributes)

    def break_dependency(self)->None:
        if not self.dependent: raise Attribute.NoDependencyIsSet
        self._dependency.release()

    @abc.abstractmethod
    def copy(self)->AbstractAttribute: pass # pragma: no cover

    def _forget_dependency(self)->None: 
        self._dependency = self.NullDependency

    @abc.abstractmethod
    def is_valid(self,value:Any)->bool: pass  # pragma: no cover

    @abc.abstractmethod
    def set(self,value:Any)->None: pass  # pragma: no cover

    def rename(self,name:str)->None: 
        if not isinstance(name,str): raise AbstractAttribute.Invalid_Name
        self.__name = name

    @abc.abstractmethod
    def on_set(
        self,
        owner:str, 
        func:Callable[[Set_Attr_Data],Command], 
        timing:Timing
        )->None:   # pragma: no cover
        
        pass
    
    @abc.abstractmethod
    def _value_update(self, new_value:Any)->None: pass   # pragma: no cover

    class Invalid_Name(Exception): pass


from typing import Iterator
Attr_List_Command_Type = Literal['append','remove']
class Attribute_List(AbstractAttribute):

    def __init__(
        self, 
        factory:Attribute_Factory, 
        atype:str, 
        name:str="",
        init_attributes:List[Any]|None = None, 
        )->None:

        super().__init__(factory, atype, name)
        self.__attributes:List[AbstractAttribute] = list()
        self._set_commands:Dict[str,Callable[[Set_Attr_Data],Command]] = dict()

        if isinstance(init_attributes,list):
            for attr_value in init_attributes:
                attr = factory.new(atype)
                attr.set(attr_value)
                self.append(attr)

    @property
    def value(self)->List[Any]: return [attr.value for attr in self.__attributes]
    @property
    def attributes(self)->List[AbstractAttribute]: return self.__attributes.copy()

    def add_dependency(self, func: Callable[[Any], Any], *attributes: AbstractAttribute) -> None:
        if any([item.dependent for item in self.__attributes]): 
            raise Attribute_List.ItemIsAlreadyDependent
        super().add_dependency(func, *attributes)
        for item in self.__attributes: 
            item._dependency = self._dependency

    def break_dependency(self)->None:
        super().break_dependency()
        for item in self.__attributes: 
            item._dependency = DependencyImpl.NULL

    def append(self,attribute:AbstractAttribute)->None:
        if isinstance(attribute, Attribute_List): 
            self._check_hierarchy_collision(attribute,self)
        self.__check_new_attribute_type(attribute)
        value_getter = lambda: self.value
        self.factory.run(
            Append_To_Attribute_List(Edit_AttrList_Data(self,attribute)),
            *self.command['set'](Set_Attr_Data(self,value_getter))
        )

    def copy(self)->Attribute_List:
        the_copy = self.factory.newlist(self.type, name=self.name)
        for item in self.__attributes:
            the_copy.__attributes.append(item.copy())
        return the_copy

    def is_valid(self,values:List[Any])->bool:
        return all([attr.is_valid(value) for attr,value in zip(self.__attributes, values)])

    def remove(self,attribute:AbstractAttribute)->None:
        if attribute not in self.__attributes: raise Attribute_List.NotInList(attribute)
        value_getter = lambda: self.value
        self.factory.run(
            Remove_From_Attribute_List(Edit_AttrList_Data(self,attribute)),
            *self.command['set'](Set_Attr_Data(self, value_getter))
        )

    def on_set(self, owner:str, func:Callable[[Set_Attr_Data],Command], timing:Timing)->None: 
        self.command['set'].add(owner, func, timing)
        self._set_commands[owner] = func

    def set(self, value:Any=None)->None:
        value_getter = lambda: self.value
        self.factory.run(*self.command['set'](Set_Attr_Data(self, value_getter)))

    def _add(self,attributes:AbstractAttribute)->None: 
        self.__attributes.append(attributes)

    @staticmethod
    def _check_hierarchy_collision(alist:Attribute_List, root_list:Attribute_List)->None:
        if alist is root_list: raise Attribute_List.ListContainsItself
        for attr in alist: 
            if isinstance(attr,Attribute_List):
                attr._check_hierarchy_collision(attr,root_list)

    def _remove(self,attributes:AbstractAttribute)->None: 
        self.__attributes.remove(attributes)

    def _value_update(self,values:List[Any])->None:
        for attr, value in zip(self.__attributes, values):
            attr._value_update(value)

   
    def __iter__(self)->Iterator[AbstractAttribute]: return self.__attributes.__iter__()
    def __getitem__(self,index:int)->AbstractAttribute: return self.__attributes[index]
    def __check_new_attribute_type(self,attr:AbstractAttribute)->None:
        if not attr.type==self.type: raise Attribute_List.WrongAttributeType(
            f"Type {attr.type} of the attribute does not match the type of the list {self.type}."
        )    

    class ItemIsAlreadyDependent(Exception): pass
    class ListContainsItself(Exception): pass
    class NotInList(Exception): pass
    class NotMatchingListLengths(Exception): pass
    class WrongAttributeType(Exception): pass


Command_Type = Literal['set']
from typing import Set, List
class Attribute(AbstractAttribute):
    default_value:Any = ""
    
    def __init__(self,factory:Attribute_Factory, atype:str='text',init_value:Any=None, name:str="")->None:  
        super().__init__(factory,atype,name)
        if init_value is not None and self.is_valid(init_value):
            self._value = init_value
        else: 
            self._value = self.default_value

    @property 
    def value(self)->Any: return self._value

    def copy(self)->Attribute:
        the_copy = self.factory.new(self.type, init_value=self._value, name=self.name)
        return the_copy

    def on_set(self, owner:str, func:Callable[[Set_Attr_Data],Command], timing:Timing)->None: 
        self.command['set'].add(owner, func, timing)

    @abc.abstractmethod
    def print(self, locale_code:Locale_Code = "en_us")->str: pass # pragma: no cover
    
    @abc.abstractmethod
    def read(self,text:str)->None: pass # pragma: no cover
        
    def set(self,value:Any)->None: 
        if self._dependency is not DependencyImpl.NULL: 
            return
        elif self.is_valid(value): 
            self._run_set_command(value)
        else:
            raise Attribute.InvalidValue(value)

    def is_valid(self, value:Any)->bool: 
        self._check_input_type(value)
        return self._is_value_valid(value)
    
    @abc.abstractmethod
    def _check_input_type(self,value:Any)->None: pass # pragma: no cover

    def _get_set_commands(self,value:Any)->List[Command]:
        value_getter = lambda: value
        return list(self.command['set'](Set_Attr_Data(self,value_getter)))

    @abc.abstractmethod
    def _is_value_valid(self,value:Any)->bool: pass # pragma: no cover

    def _run_set_command(self,value:Any)->None:
        self.factory.controller.run(*self._get_set_commands(value))
    
    def _value_update(self,value:Any)->None:
        self._value = value
    
    @staticmethod
    def set_multiple(new_values:Dict[Attribute,Any])->None:
        facs:List[Attribute_Factory] = list()
        cmds:List[List[Command]] = list()
        for attr,value in new_values.items():
            if attr.dependent: continue #ignore dependent attributes
            if not attr.factory in facs: # Attribute_Factory is not hashable, two lists circumvent the problem
                facs.append(attr.factory)
                cmds.append(list())
            cmds[facs.index(attr.factory)].extend(attr._get_set_commands(value))
        
        for fac, cmd_list in zip(facs,cmds):
            fac.controller.run(*cmd_list)

    class DependencyAlreadyAssigned(Exception): pass
    class InvalidAttributeType(Exception): pass
    class InvalidDefaultValue(Exception): pass
    class InvalidValueType(Exception): pass
    class InvalidValue(Exception): pass
    class NoDependencyIsSet(Exception): pass


class Number_Attribute(Attribute):
    default_value = 0
    class CannotExtractNumber(Exception): pass
    _reading_exception:Type[Exception] = CannotExtractNumber

    @abc.abstractmethod
    def _check_input_type(self, value: Any) -> None:  # pragma: no cover
        return super()._check_input_type(value)

    @abc.abstractmethod # pragma: no cover
    def print(
        self, 
        locale_code:Locale_Code = "en_us",
        use_thousands_separator:bool=False
        )->str:

        pass

    def read(self, text:str)->None:
        text = text.strip().replace(",",".")
        text = self.remove_thousands_separators(text)
        try:
            value = Decimal(text)
            if not self.is_valid(value): raise
            else: self.set(value)
        except:
            raise self._reading_exception

    __Comma_Separator:Set[str] = {"cs_cz",}
    @staticmethod
    def _adjust_decimal_separator(value:str,locale_code:str)->str:
        if locale_code in Number_Attribute.__Comma_Separator:
            value = value.replace('.',',')
        return value

    @staticmethod
    def _set_thousands_separator(value_str:str,use_thousands_separator:bool)->str:
        if use_thousands_separator: return value_str.replace(',',NBSP)
        else: return value_str.replace(',','')

    @staticmethod
    def is_int(value)->bool: return int(value)==value

    @staticmethod
    def remove_thousands_separators(value_str:str)->str:
        for sep in (' ',NBSP,'\t'):  value_str = value_str.replace(sep,'')
        return value_str


class Integer_Attribute(Number_Attribute):
    class CannotExtractInteger(Exception): pass
    _reading_exception:Type[Exception] = CannotExtractInteger

    def _check_input_type(self, value: Any) -> None:
        try: 
            if not int(value)==value: raise
        except: raise Attribute.InvalidValueType(type(value))

    def _is_value_valid(self, value:Any)->bool: return True
        
    def print(
        self, 
        locale_code:Locale_Code = "en_us",
        use_thousands_separator:bool=False
        )->str:

        value_str = f'{self._value:,}'
        value_str = self._set_thousands_separator(value_str, use_thousands_separator)
        return value_str

    
import math
class Real_Attribute(Number_Attribute):
    class CannotExtractReal(Exception): pass
    _reading_exception:Type[Exception] = CannotExtractReal

    def __init__(self,factory:Attribute_Factory, atype:str,init_value:Any=None,name:str="")->None:
        if init_value is not None and self.is_valid(init_value):
            init_value = Decimal(str(init_value))
        super().__init__(factory,atype,init_value,name)

    def _check_input_type(self, value: Decimal|float|int) -> None:
        try: 
            if math.isnan(float(value)): return
            elif not Decimal(value)==value: raise
        except: 
            raise Attribute.InvalidValueType(type(value))

    def _is_value_valid(self, value:Any)->bool:
        return True

    def print(
        self,
        locale_code:Locale_Code = "en_us",
        use_thousands_separator:bool=False,
        precision:int=28,
        trailing_zeros:bool=True
        )->str:
        
        str_value = format(self._value, f',.{precision}f')
        str_value = self._set_thousands_separator(str_value, use_thousands_separator)
        if not trailing_zeros: str_value = str_value.rstrip('0').rstrip('.')
        str_value = self._adjust_decimal_separator(str_value, locale_code)
        return str_value
        
    def set(self,value:Decimal|float|int)->None:
        if self.is_valid(value):
            value = Decimal(str(value))
            self._run_set_command(value)
        else: # pragma: no cover
            raise Attribute.InvalidValue(value)
    

Currency_Code = Literal['USD','EUR','CZK','JPY']
Currency_Symbol = Literal['$','€','Kč','¥']
@dataclasses.dataclass
class Currency:
    code:Currency_Code
    symbol:Currency_Symbol
    decimals:Literal[0,2] = 2
    symbol_before_value:bool = True

class Monetary_Attribute(Number_Attribute):
    __currencies:Dict[Currency_Code,Currency] = {
        'USD':Currency('USD','$'),
        'EUR':Currency('EUR','€'),
        'CZK':Currency('CZK','Kč',symbol_before_value=False),
        'JPY':Currency('JPY','¥',decimals=0)
    }
    @staticmethod
    def preferred_symbol_before_value(locale_code:str)->bool:
        preferred_by:Set[Locale_Code] = {'en_us'}
        return locale_code in preferred_by
    
    def _check_input_type(self, value:float|int|Decimal) -> None:
        try: 
            if math.isnan(float(value)): return
            if not Decimal(value)==value: raise
        except: raise Attribute.InvalidValueType(type(value))

    def _is_value_valid(self, value:float|int|Decimal)->bool:
        return True

    def set(self,value:float|Decimal)->None:
        # For the sake of clarity, the input to the set method has to be kept in the same type as the 
        # '_value' attribute.

        # The string must then be explicitly excluded from input types, as it would normally be 
        # accepted by the Decimal.
        if isinstance(value, str): 
            raise Attribute.InvalidValueType(value)
        super().set(Decimal(str(value)))

    def print(
        self,
        locale_code:Locale_Code = 'en_us',
        use_thousands_separator:bool = False,
        currency_code:Currency_Code = "USD",
        trailing_zeros:bool = True,
        enforce_plus:bool = False
        )->str:
    
        locale = verify_and_format_locale_code(locale_code)
        if not currency_code in self.__currencies: raise self.CurrencyNotDefined
        currency = self.__currencies[currency_code]

        if not trailing_zeros and int(self._value)==self._value: n_places = 0
        else: n_places = self.__currencies[currency_code].decimals
        value_str = format(round(self._value,n_places), ',.'+str(n_places)+'f')
        value_str = self._set_thousands_separator(value_str, use_thousands_separator)
        # decimal separator is adjusted AFTER setting thousands separator to avoid collisions when comma 
        # is used for one or the other
        value_str = self._adjust_decimal_separator(value_str,locale)
        value_str = self.__add_symbol_to_printed_value(value_str, locale, currency)
        if enforce_plus and self._value>0: value_str = '+'+value_str
        return value_str

    def read(self,text:str)->None:
        text = text.strip()
        text = self.remove_thousands_separators(text)
        if text=="":  raise self.ReadingBlankText
        sign, symbol, value = self.__extract_sign_symbol_and_value(text)
        self.set(Decimal(sign+value))

    SYMBOL_PATTERN = "(?P<symbol>[^\s\d\.\,]+)"
    VALUE_PATTERN = "(?P<value>[0-9]+([\.\,][0-9]*)?)"
    SYMBOL_FIRST = f"({SYMBOL_PATTERN}{VALUE_PATTERN})"
    VALUE_FIRST = f"({VALUE_PATTERN}[ \t{NBSP}]?{SYMBOL_PATTERN})"

    @staticmethod
    def __extract_sign_symbol_and_value(text:str)->Tuple[str,str,str]:
        sign, text = Monetary_Attribute.__extract_sign(text)
        thematch = re.match(Monetary_Attribute.SYMBOL_FIRST ,text)
        if thematch is None: thematch = re.match(Monetary_Attribute.VALUE_FIRST ,text)
        if thematch is None: 
            raise Monetary_Attribute.CannotExtractValue(text)
        if thematch['symbol'] not in get_args(Currency_Symbol): 
            raise Monetary_Attribute.UnknownCurrencySymbol(thematch['symbol'])
        return sign, thematch['symbol'], thematch['value'].replace(",",".")

    @staticmethod
    def __extract_sign(text:str)->Tuple[str,str]:
        if text[0] in ("+","-"): sign,text = text[0],text[1:]
        else: sign = "+"
        return sign, text

    @classmethod
    def __add_symbol_to_printed_value(
        cls,
        value:str,
        locale_code:str, 
        currency:Currency
        )->str:
        
        if cls.preferred_symbol_before_value(locale_code) and currency.symbol_before_value: 
            if value[0] in ('-','+'): value_str = value[0] + currency.symbol + value[1:]
            else: value_str = currency.symbol + value
        else: 
            value_str = value + NBSP + currency.symbol
        return value_str
    
    class CannotExtractValue(Exception): pass
    class CurrencyNotDefined(Exception): pass
    class ReadingBlankText(Exception): pass
    class UnknownCurrencySymbol(Exception): pass


class Text_Attribute(Attribute):

    def _check_input_type(self, value: Any) -> None:
        if not isinstance(value,str): raise Attribute.InvalidValueType(type(value))

    def _is_value_valid(self,value:Any)->bool:
        return True
    
    def print(self, *options)->str:
        return str(self._value)
    
    def read(self, text:str)->None:
        self.set(text)


import datetime
import re

class Date_Attribute(Attribute):
    default_value = datetime.date.today()
    # all locale codes must be entered in lower case 
    __date_formats:Dict[str,str] = {
        'cs_cz':'%d.%m.%Y',
        'en_us':'%Y-%m-%d'
    }

    DEFAULT_SEPARATOR = "-"
    SEPARATOR = "[\.\,\-_]"
    YEARPATT = "(?P<year>[0-9]{3,4})"
    MONTHPATT = "(?P<month>0?[1-9]|1[0-2])"
    DAYPATT = "(?P<day>0?[1-9]|[12][0-9]|3[01])"

    YMD_PATT = YEARPATT + SEPARATOR + MONTHPATT + SEPARATOR + DAYPATT
    DMY_PATT = DAYPATT + SEPARATOR + MONTHPATT + SEPARATOR + YEARPATT

    def _check_input_type(self, value: Any) -> None:
        if not isinstance(value, datetime.date): 
            raise Attribute.InvalidValueType(type(value))

    def _is_value_valid(self, value: Any) -> bool:
        return True

    def is_valid(self, value: Any) -> bool:
        self._check_input_type(value)
        return self._is_value_valid(value)
    
    def print(self, locale_code:Locale_Code="en_us",*options)->str:
        locale = verify_and_format_locale_code(locale_code)
        date_format = self.__date_formats[locale]
        return datetime.date.strftime(self._value,date_format)
    
    def read(self,text:str)->None:
        text = self.__remove_spaces(text)
        date_match = re.fullmatch(self.YMD_PATT, text)
        if date_match is None: date_match = re.fullmatch(self.DMY_PATT, text)
        if date_match is None: raise Date_Attribute.CannotExtractDate(text)
        date = date_match.groupdict()
        year, month, day = map(int,(date['year'], date['month'], date['day']))
        self.set(datetime.date(year, month, day))

    def __remove_spaces(self,text:str)->str: 
        for sp in (" ",NBSP,"\t"): text = text.replace(sp, "")
        return text
    
    class CannotExtractDate(Exception): pass



from src.utils.naming import strip_and_join_spaces
class Choice_Attribute(Attribute):
    default_value = ""

    def __init__(self, factory:Attribute_Factory, name:str="")->None:
        self.options:List[Any] = list()
        super().__init__(factory, atype='choice', name=name)

    @property
    def value(self)->Any: 
        if self.options: return self._value
        else: raise Choice_Attribute.NoOptionsAvailable

    def add_options(self, *options:Any)->None:
        for op in options:
            if isinstance(op,str):
                op = strip_and_join_spaces(op)
            if op not in self.options: # prevent duplicities
                self.options.append(op)
        # finding duplicate after converting all options to strings 
        # means the same option occured, only with different type 
        stringified_ops = set(map(str,self.options))
        if len(stringified_ops)<len(self.options): 
            raise Choice_Attribute.DuplicateOfDifferentType(self.options)
        if self._value=='': self._value = options[0]

    def clear_options(self)->None:
        self.options.clear()

    def _check_input_type(self, value: Any) -> None: 
        pass

    def _is_value_valid(self,value:Any)->bool: 
        if value not in self.options: 
            raise Choice_Attribute.UndefinedOption(
                f"Unknown option: {value}; available options are: {self.options}"
            )
        return value in self.options

    def is_option(self, value:Any)->bool:
        return value in self.options

    def print(
        self,
        locale_code:Locale_Code = "en_us",
        lower_case:bool = False
        )->str:

        return self._str_value(self._value,lower_case)

    def print_options(self, lower_case:bool=False)->Tuple[str,...]:
        result = tuple([self._str_value(op, lower_case) for op in self.options])
        return result

    def read(self, text:str)->None:
        text = text.strip()
        for op in self.options:
            if str(op)==text: 
                self.set(op) 
                return
        raise Choice_Attribute.UndefinedOption(
            f"Unknown option: {text}; available options are: {self.options}"
        )

    def remove_options(self,*options:Any)->None:
        if self._value in options: 
            raise Choice_Attribute.CannotRemoveChosenOption(self._value)
        for op in options:
            if op in self.options: 
                self.options.remove(op)
            else: 
                raise Choice_Attribute.UndefinedOption(
                    f"Unknown option: {op}; available options are: {self.options}"
                )

    def set(self,value:Any)->None:
        if not self.options: raise Choice_Attribute.NoOptionsAvailable
        super().set(value)
    
    @classmethod
    def _str_value(cls, value, lower_case:bool=False) -> str:
        return str(value).lower() if lower_case else str(value)

    class CannotRemoveChosenOption(Exception): pass
    class DuplicateOfDifferentType(Exception): pass
    class NoOptionsAvailable(Exception): pass
    class UndefinedOption(Exception): pass


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
        self.types['money'] = Monetary_Attribute

    def newlist(self,atype:str='text', init_items:List[Any]|None=None, name:str="")->Attribute_List:
        if atype not in self.types: raise Attribute.InvalidAttributeType(atype)
        return Attribute_List(self, atype, init_attributes=init_items, name=name)

    def new(self,atype:str='text',init_value:Any=None, name:str="")->Attribute:
        if atype not in self.types: raise Attribute.InvalidAttributeType(atype)
        else:
            return self.types[atype](self,atype,init_value,name)
        
    def choice(self, name:str="")->Choice_Attribute:
        return Choice_Attribute(self,name)
        
    def add(self,label:str,new_attribute_class:Type[Attribute])->None:
        if label in self.types:
            raise Attribute_Factory.TypeAlreadyDefined(
                f"Label '{label}' already assigned to attribute class '{self.types[label]}'."
            )
        else:
            self.types[label] = new_attribute_class


    def redo(self)->None: self.controller.redo()
    def run(self,*cmds:Command)->None:
        self.controller.run(*cmds)
    
    def undo(self)->None: self.controller.undo()

    class TypeAlreadyDefined(Exception): pass


def attribute_factory(controller:Controller)->Attribute_Factory:
    return Attribute_Factory(controller)
