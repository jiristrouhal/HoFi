from __future__ import annotations
from typing import Any, Callable, Protocol, Dict, Literal, Tuple

import abc
import re


class AttributesOwner(Protocol):

    @property
    def attributes(self)->Dict[str,_Attribute]: ...



class _Attribute(abc.ABC):
    default_value:Any = None

    def __init__(self, value:Any = None)->None:
        if value is None or not self.valid_entry(value): 
            self._value = self.default_value
        else:
            self._value = value

    @abc.abstractproperty
    def value(self)->Any: pass
    @abc.abstractproperty
    def formatted_value(self)->str: pass

    @staticmethod
    @abc.abstractmethod
    def valid_entry(value:str)->bool: pass

    @abc.abstractmethod
    def copy(self)->_Attribute:
        pass

    def set(self,value:str="")->None:
        if self.valid_entry(value) and not str(value).strip()=="": 
            self._value = str(value)


from functools import partial
class Dependent_Attr(_Attribute):
    default_value = ""
    def __init__(self, foo:Callable[[AttributesOwner],Any])->None:
        super().__init__(foo)
        self._owner_has_been_set = False
    @property
    def value(self)->Any: return self._value()
    @property
    def formatted_value(self)->str:
        return self.value
    @staticmethod
    def valid_entry(value:str)->bool: return True

    def set_owner(self,obj:AttributesOwner)->None:
        if not self._owner_has_been_set:
            self._value = partial(self._value,obj)
            self._owner_has_been_set = True

    def copy(self)->Dependent_Attr:
        return Dependent_Attr(self._value)
    

class Positive_Int_Attr(_Attribute):
    default_value = "1"
    @property
    def value(self)->int: return int(self._value)
    @property
    def formatted_value(self)->str:
        return str(self.value)
    @staticmethod
    def valid_entry(value:str)->bool: 
        if value=="": return True
        if re.fullmatch("\d+",str(value)) is None: return False
        return int(value)>0
    
    def copy(self)->Positive_Int_Attr:
        return Positive_Int_Attr(self._value)
    

import decimal
from decimal import Decimal, Context
from dataclasses import dataclass


Curry_Symbol_Position = Literal[0,1]
Localization_Code = Literal['en_US', 'cs_CZ']
CURRY_SYMBOL_POSITION:Dict[Localization_Code,Curry_Symbol_Position] = {
    'en_US':0,
    'cs_CZ':1
}
CURRY_CODE_BY_LOCALIZATION:Dict[Localization_Code,Currency_Code] = {
    'en_US': 'USD',
    'cs_CZ': 'CZK'
}

LOCALIZATION_CODE = 'en_US'
DEFAULT_CURRENCY_CODE = CURRY_CODE_BY_LOCALIZATION[LOCALIZATION_CODE]

def set_localization(code:Localization_Code)->None:
    global LOCALIZATION_CODE, DEFAULT_CURRENCY_CODE
    LOCALIZATION_CODE = code
    DEFAULT_CURRENCY_CODE = CURRY_CODE_BY_LOCALIZATION[LOCALIZATION_CODE]


@dataclass
class _Curry_Format:
    decimals:Literal[0,1,2,3]
    symbol:str
    prepend:bool = True
    def __post_init__(self):
        self.context = Context(prec=self.decimals,rounding=decimal.ROUND_HALF_EVEN)

    def present(self,value:Decimal|float|str)->str:
        value =  round(Decimal(str(value),self.context), self.decimals)
        if CURRY_SYMBOL_POSITION[LOCALIZATION_CODE]==0 and self.prepend:
            return self.__prepend_symbol(value)
        else:
            return self.__append_symbol(value)

    def __prepend_symbol(self,value:Decimal|float|str)->str:
        return self.symbol+str(value)

    def __append_symbol(self,value:Decimal|float|str)->str:
        return str(value) + ' ' + self.symbol
        


Currency_Code = Literal['CZK','EUR', 'USD']
CURRY_FORMATS:Dict[Currency_Code,_Curry_Format] = {
    'CZK':_Curry_Format(2,'Kč',prepend=False),
    'EUR':_Curry_Format(2,'€'),
    'USD': _Curry_Format(2,'$')
}
CURRENCY_SYMBOLS = [CURRY_FORMATS[code].symbol for code in CURRY_FORMATS]
CURR_SYMBOLS_TO_CODE = {CURRY_FORMATS[code].symbol:code for code in CURRY_FORMATS}

class UndefinedCurrency(Exception): pass

class Currency_Attribute(_Attribute):

    default_value = "1"
    rounding = decimal.ROUND_HALF_EVEN
    localization:Curry_Symbol_Position = 0

    def __init__(self, currency_code:Currency_Code, value:Any=default_value)->None:
        super().__init__(value)
        self._currency_code = currency_code
        self._decimal_context = Context(
            prec=CURRY_FORMATS[currency_code].decimals, 
            rounding = Currency_Attribute.rounding
        )
    @property
    def value(self)->Decimal:
        return Decimal(self._value)
    @property
    def formatted_value(self)->str:
        return CURRY_FORMATS[self._currency_code].present(self._value)

    @staticmethod
    def valid_entry(value:str) -> bool:
        try: return float(value)>0
        except: return False
    
    def copy(self)->Currency_Attribute:
        return Currency_Attribute(self._currency_code,self._value)
    
    def set_currency(self,currency_code:Currency_Code)->None:
        if currency_code not in CURRY_FORMATS: 
            raise UndefinedCurrency(
                f"Cannot set currency. Code {currency_code} is not defined."
            )
        self._currency_code = currency_code
    


import datetime, src.core.dates
class Date_Attr(_Attribute):
    default_value = datetime.date.today()
    date_formatter = src.core.dates.get_date_converter("%d.%m.%Y")

    def __init__(self, value:str|None=None)->None:
        if value is not None and self.final_validation(value):
            self._value = self.date_formatter.enter_date(value)
        else:
            self._value = self.default_value

    @property
    def value(self)->str: 
        return self.date_formatter.print_date(self._value)
    @property
    def formatted_value(self)->str:
        return self.value
    
    @staticmethod
    def valid_entry(value:str)->bool: 
        if value.strip()=="": return True
        if re.fullmatch("[\d\._\- ]*",value): return True
        return False
    
    @staticmethod
    def final_validation(value:str)->bool:
        if value.strip()=="": return True
        return Date_Attr.date_formatter.validate_date(value)
    
    def copy(self)->Date_Attr:
        return Date_Attr(self.value)
    
    def set(self,value:str="")->None:
        if self.final_validation(value) and not str(value).strip()=="":
            self._value = self.date_formatter.enter_date(value)


class Name_Attr(_Attribute):
    default_value = "New"
    @property
    def value(self)->str: return str(self._value)
    @property
    def formatted_value(self)->str:
        return self.value
    @staticmethod
    def valid_entry(value:str)->bool: 
        if value=="": return True
        if re.fullmatch("[^\W\d].*",str(value)) is None: return False
        return True

    def copy(self)->Name_Attr:
        return Name_Attr(self._value)
    

class Text_Attr(_Attribute):
    default_value = "Text"
    @property
    def value(self)->str: return str(self._value)
    @property
    def formatted_value(self)->str:
        return self.value
    @staticmethod
    def valid_entry(value:str)->bool: return True

    def copy(self)->Text_Attr:
        return Text_Attr(self._value)
    


def create_attribute(value:Any)->_Attribute:
    if callable(value):
        return Dependent_Attr(value)
    elif Positive_Int_Attr.valid_entry(value):
        return Positive_Int_Attr(value)
    possible_currency = convert_to_currency(value)
    if possible_currency:
        amount = possible_currency[0]
        currency_code = possible_currency[1]
        return Currency_Attribute(currency_code,amount)
    elif Date_Attr.valid_entry(value):
        return Date_Attr(Date_Attr.date_formatter.print_date(datetime.date.today()))
    elif Name_Attr.valid_entry(value):
        return Name_Attr(value)
    else:
        return Text_Attr(value)


def convert_to_currency(text:str)->Tuple[str,str]|Tuple:
    text = str(text).strip()
    if re.fullmatch("\d+([\.\,]\d*)?\s*\S*",text) is not None or re.fullmatch("[\.\,]\d+\s*\S*",text) is not None:
        i = 0
        while i<len(text) and (text[i].isdigit() or text[i] in ('.',',')):  
            i += 1
        text_without_number = text[i:].strip()
        if text_without_number in CURRENCY_SYMBOLS:
            currency_code = CURR_SYMBOLS_TO_CODE[text_without_number]
            return (text[i:], currency_code)
        return ()
    
    elif re.fullmatch("\S*\s*\d+([\.\,]\d*)?",text) is not None:
        i = -1
        while  i>-len(text)-1 and (text[i].isdigit() or text[i] in ('.',',')):
            i -= 1
        text_without_number = text[:i+1].strip()
        if text_without_number in CURRENCY_SYMBOLS:
            currency_code = CURR_SYMBOLS_TO_CODE[text_without_number]
            return (text[i:], currency_code)
        return ()
    
    return ()
