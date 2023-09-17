from __future__ import annotations

from typing import Literal, Any, Callable, get_args
import abc
import dataclasses

from src.cmd.commands import Command, Composed_Command, Timing, Dict, Controller


NBSP = u"\u00A0"


from decimal import Decimal, getcontext
getcontext().prec = 28
Locale_Code = Literal['cs_cz','en_us']
class UnknownLocaleCode(Exception): pass
def verify_and_format_locale_code(locale_code:Locale_Code)->str:
    locale = locale_code.lower()
    if not locale in get_args(Locale_Code): raise UnknownLocaleCode(locale)
    return locale.lower()



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

    @abc.abstractmethod
    def print(self, *options)->str: pass # pragma: no cover
    
    @abc.abstractmethod
    def read(self,text:str)->None: # pragma: no cover
        pass
        
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
        if not self.is_valid(value): 
            raise Attribute.InvalidValueType(value)
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
        self.types['money'] = Monetary_Attribute

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


class Integer_Attribute(Attribute):
    default_value = 0

    def is_valid(self, value:Any) -> bool:
        try: return int(value) == value
        except: return False
        
    def print(self, thousands_sep:bool=False, *options)->str:
        if thousands_sep:
            return f'{self._value:,}'.replace(",",NBSP)
        return str(self._value)

    def read(self,text:str)->None:
        text = text.strip().replace(",",".")
        try:
            float_value = float(text)
            if int(float_value)==float_value:
                self.is_valid(float_value)
                self.set(float_value)
            else:
                raise
        except:
            raise Integer_Attribute.CannotExtractInteger(text)

    class CannotExtractInteger(Exception): pass
        

__Comma_Separator:Set[str] = {"cs_cz",}
def _use_comma_as_decimal_separator(locale_code:str)->bool:
    return locale_code in __Comma_Separator

    
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
        
    def print(
        self,
        precision:int=28,
        trailing_zeros:bool=True,
        locale_code:Locale_Code = "en_us",
        thousands_sep:bool=False,
        *options:Any
        )->str:
        
        tsep = NBSP if thousands_sep else ''
        str_value = format(self._value, f',.{precision}f').replace(",",tsep)
        if not trailing_zeros: str_value = str_value.rstrip('0').rstrip('.')
        if _use_comma_as_decimal_separator(locale_code): str_value = str_value.replace('.',',')
        return str_value
        
    def read(self, text:str)->None:
        text = text.strip().replace(",",".")
        try:
            self.set(Decimal(text))
        except:
            raise Real_Attribute.CannotExtractNumber(text)
        
    def set(self,value:Decimal|float|int)->None:
        value = Decimal(str(value))
        super().set(value)
    
    @staticmethod
    def is_int(value)->bool: return int(value)==value
    
    class CannotExtractNumber(Exception): pass


class Monetary_Attribute(Attribute):
    default_value = Decimal('0')
    __curr_symbols = {
        'USD':'$',
        'JPY':'¥',
        'CZK': 'Kč',
    }
    __symbol_before_value:Set[str] = {"en_us",}
    __special_decimal_places = {'JPY':0}
    __DEFAULT_DECIMALS = 2

    def set(self,value:float|Decimal)->None:
        # For the sake of clarity, the input to the set method has to be kept in the same type as the 
        # '_value' attribute.

        # The string must then be explicitly excluded from input types, as it would normally be 
        # accepted by the Decimal.
        if isinstance(value, str): raise Attribute.InvalidValueType
        super().set(Decimal(str(value)))

    def add(self,value:Decimal|float|int)->None:
        try: self.set(self.value + Decimal(str(value)))
        except: raise Monetary_Attribute.InvalidIncrement

    def subtract(self,value:Decimal|float|int)->None:
        try: self.set(self.value - Decimal(str(value)))
        except: raise Monetary_Attribute.InvalidDecrement

    def print(
        self,
        locale_code:Locale_Code = 'en_us',
        currency:str = "USD",
        trailing_zeros:bool = True,
        enforce_plus:bool = False,
        use_thousands_separator:bool = False,
        *options:Any
        )->str:
    
        value = self._value

        locale = verify_and_format_locale_code(locale_code)
        if not trailing_zeros and int(value)==value: n_places = 0
        else: n_places = self.__n_of_decimals(currency)
        value_str = format(round(value,n_places), ',.'+str(n_places)+'f')
        value_str = self.__set_thousands_separator(value_str, use_thousands_separator)
        value_str = self.__adjust_decimal_separator(value_str,locale)
        value_str = self.__add_symbol(value_str, locale, currency)
        if enforce_plus and value>0: value_str = '+'+value_str
        return value_str

    def is_valid(self, value: Any)->bool:
        try: return Decimal(value) == value
        except: return False

    def read(self,text:str)->None:
        text = text.strip()
        self.__catch_blank(text)
        sign, symbol, value = self.__extract_sign_symbol_and_value(text)
        if symbol not in self.__curr_symbols.values():
            raise self.UnknownCurrencySymbol(symbol)
        self.set(Decimal(sign+value))

    def __catch_blank(self,text:str)->None:
        if text=="":  raise self.ReadingBlankText

    SYMBOL_PATTERN = "(?P<symbol>[^\s\d\.\,]+)"
    VALUE_PATTERN = "(?P<value>[0-9]+([\.\,][0-9]*)?)"
    SYMBOL_FIRST = f"({SYMBOL_PATTERN}{VALUE_PATTERN})"
    VALUE_FIRST = f"({VALUE_PATTERN}[ \t{NBSP}]?{SYMBOL_PATTERN})"

    def __extract_sign_symbol_and_value(self,text:str)->Tuple[str,str,str]:
        sign, text = self.__extract_sign(text)
        thematch = re.match(self.SYMBOL_FIRST ,text)
        if thematch is None: thematch = re.match(self.VALUE_FIRST ,text)
        if thematch is None: raise self.CannotExtractValue
        return sign, thematch['symbol'], thematch['value'].replace(",",".")

    def __extract_sign(self,text:str)->Tuple[str,str]:
        if text[0] in ("+","-"): sign,text = text[0],text[1:]
        else: sign = "+"
        return sign, text

    @staticmethod
    def __adjust_decimal_separator(value:str,locale_code:str)->str:
        if _use_comma_as_decimal_separator(locale_code):
            value = value.replace('.',',')
        return value
    
    @classmethod
    def __add_symbol(cls,value:str,locale_code:str, currency:str)->str:
        if currency in cls.__curr_symbols: symbol = cls.__curr_symbols[currency]
        else: raise cls.UnknownCurrencySymbol
        symbol = cls.__curr_symbols[currency]

        if locale_code in cls.__symbol_before_value: 
            if value[0] in ('-','+'): value_str = value[0] + symbol + value[1:]
            else: value_str = symbol + value
        else: 
            value_str = value + NBSP + symbol
        return value_str

    @classmethod
    def __set_thousands_separator(cls,value_str:str,use_thousands_separator:bool)->str:
        if use_thousands_separator: value_str = value_str.replace(',',NBSP)
        else: value_str = value_str.replace(',','')
        return value_str
    
    @classmethod
    def __n_of_decimals(cls,currency:str)->int:
        if currency in cls.__special_decimal_places:
            return cls.__special_decimal_places[currency]
        else:
           return cls.__DEFAULT_DECIMALS


    class CannotExtractValue(Exception): pass
    class InvalidDecrement(Exception): pass
    class InvalidIncrement(Exception): pass
    class ReadingBlankText(Exception): pass
    class UnknownCurrencySymbol(Exception): pass



class Text_Attribute(Attribute):
    default_value = ""
    printops:Dict[str,Any] = {}

    def is_valid(self, value:Any) -> bool:
        return isinstance(value,str)
    
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
    OTHER_SEPARATORS = (".",",","_")
    YEARPATT = "[0-9]{3,4}"
    MONTHPATT = "(0?[1-9]|1[0-2])"
    DAYPATT = "(0?[1-9]|[12][0-9]|3[01])"
    SEPARATOR = "-"

    YMD_PATT = YEARPATT + SEPARATOR + MONTHPATT + SEPARATOR + DAYPATT
    DMY_PATT = DAYPATT + SEPARATOR + MONTHPATT + SEPARATOR + YEARPATT

    def is_valid(self, value: Any) -> bool:
        return isinstance(value, datetime.date)
    
    def print(self, locale_code:Locale_Code="en_us",*options)->str:
        locale = verify_and_format_locale_code(locale_code)
        date_format = self.__date_formats[locale]
        return datetime.date.strftime(self._value,date_format)
    
    def read(self,text:str)->None:
        text = self.__remove_spaces(text)
        for sep in self.OTHER_SEPARATORS: 
            text = text.replace(sep, self.SEPARATOR)
        if re.fullmatch(self.YMD_PATT, text): 
            raw = list(map(int,text.split(self.SEPARATOR)))
            date = datetime.date(year=raw[0],month=raw[1],day=raw[2])
        elif re.fullmatch(self.DMY_PATT, text):
            raw = list(map(int,text.split(self.SEPARATOR)))
            date = datetime.date(year=raw[2],month=raw[1],day=raw[0]) 
        else: 
            raise Date_Attribute.CannotExtractDate
        self.set(date)

    def __remove_spaces(self,text:str)->str: return text.replace(" ", "")
    
    class CannotExtractDate(Exception): pass



from src.utils.naming import strip_and_join_spaces
class Choice_Attribute(Attribute):
    default_value = ""
    printops:Dict[str,Any] = {'lower_case':False}

    def __init__(self, factory:Attribute_Factory, atype:str, name:str="")->None:
        self.options:List[Any] = list()
        super().__init__(factory, atype, name)

    @property
    def value(self)->Any: 
        if self.options: return self._value
        else: raise Choice_Attribute.OptionsNotDefined

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
            raise Choice_Attribute.DuplicateOfDifferentType
        if self._value=='': self._value = options[0]

    def clear_options(self)->None:
        self.options.clear()

    def print(self,lower_case:bool = False, *format_options)->str:
        return self._str_value(self._value,lower_case,*format_options)

    def print_options(self, lower_case:bool=False)->Tuple[str,...]:
        result = tuple([self._str_value(op, lower_case) for op in self.options])
        return result

    def read(self, text:str)->None:
        text = text.strip()
        for op in self.options:
            if str(op)==text: 
                self.set(op) 
                return
        raise Choice_Attribute.NonexistentOption

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
    def _str_value(cls, value, lower_case:bool=False, *format_options) -> str:
        return str(value).lower() if lower_case else str(value)

    class CannotRemoveChosenOption(Exception): pass
    class DuplicateOfDifferentType(Exception): pass
    class NonexistentOption(Exception): pass
    class OptionsNotDefined(Exception): pass
