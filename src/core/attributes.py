from __future__ import annotations
from typing import Any, Callable, Protocol, Dict, List

import abc
import re

from functools import partial


from src.lang.lang import Locale_Code


import decimal
from decimal import Decimal, Context
import src.core.currency as cur

import datetime
import src.core.dates as dates


class Attribute_Factory:

    def __init__(self,locale_code:Locale_Code)->None:
        self.__locale_code = locale_code

    @property
    def locale_code(self)->str: return self.__locale_code

    def set_locale_code(self,code:Locale_Code)->None:
        self.__locale_code = code

    def create_attribute(self, default_value:Any,options:Dict[str,Any]={})->_Attribute:
        if callable(default_value):
            return Dependent_Attr(default_value,locale_code=self.__locale_code)
        
        elif options:
            return Choice_Attribute(default_value, options,locale_code=self.__locale_code)

        elif Positive_Int_Attr.valid_entry(default_value):
            return Positive_Int_Attr(default_value,locale_code=self.__locale_code)
        
        possible_currency = cur.convert_to_currency(default_value)
        if possible_currency:
            amount = possible_currency[0]
            currency_code = possible_currency[1]
            return Currency_Attribute(currency_code,amount,locale_code=self.__locale_code)
        
        elif dates.validate_date(default_value, dates.DATE_FORMATS[self.__locale_code]):
            return Date_Attr(
                dates.date_to_str(datetime.date.today(), dates.DATE_FORMATS[self.__locale_code]),
                locale_code=self.__locale_code
            )
        
        elif Name_Attr.valid_entry(default_value):
            return Name_Attr(default_value,locale_code=self.__locale_code)
        
        else:
            return Text_Attr(default_value,locale_code=self.__locale_code)



class AttributesOwner(Protocol):

    @property
    def attributes(self)->Dict[str,_Attribute]: ...


class _Attribute(abc.ABC):
    default_value:Any = None

    def __init__(self, value:Any = None, value_options:Dict[str,Any]={}, locale_code:Locale_Code="en_us")->None:
        if value is None: 
            self._value = self.default_value
        else:
            self._value = value

        self._value_options = value_options
        self._locale_code = locale_code

        self.choice_actions:Dict[str,Callable[[Any],None]] = dict()
        self.choices:Dict[str,List[Any]] = dict()
        self.selected_choices:Dict[str,Any] = dict()

    @abc.abstractproperty
    def value(self)->Any: pass
    @abc.abstractproperty
    def formatted_value(self)->str: pass
    @property
    def options(self)->List[str]: return list(self._value_options.keys())

    @staticmethod
    @abc.abstractmethod
    def valid_entry(value:str)->bool: pass

    @abc.abstractmethod
    def copy(self)->_Attribute:
        pass

    def set(self,value:str="")->None:
        if self.valid_entry(value) and not str(value).strip()=="": 
            self._value = str(value)


class Choice_Attribute(_Attribute):
    is_choice:bool = True
    def __init__(self, default:str, options:Dict[str,Any], locale_code:Locale_Code = "en_us")->None:
        if default not in options: 
            raise KeyError(f"Cannot initialize Choice attribute with option '{default}',"
                           f" which not present in the options passed {tuple(options.keys())}.")
        super().__init__(default,locale_code=locale_code)
        self._value_options = options
    
    @property
    def value(self)->Any: return self._value_options[self._value]
    @property
    def options(self)->List[str]: return list(self._value_options.keys())
    @property
    def formatted_value(self)->str:
        return self._value
    @staticmethod
    def valid_entry(value:str)->bool: return True

    def copy(self)->Choice_Attribute:
        return Choice_Attribute(self._value, self._value_options, locale_code=self._locale_code)


class Dependent_Attr(_Attribute):
    default_value = ""
    def __init__(self, foo:Callable[[AttributesOwner],Any], locale_code:Locale_Code = "en_us")->None:
        super().__init__(foo,locale_code=locale_code)
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
        return Dependent_Attr(self._value, locale_code=self._locale_code)
    

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
        return Positive_Int_Attr(self._value, locale_code=self._locale_code)


class Currency_Attribute(_Attribute):

    default_value = "1"
    rounding = decimal.ROUND_HALF_EVEN
    localization:cur.Curry_Symbol_Position = 0

    def __init__(self, currency_code:cur.Currency_Code, value:Any=default_value, locale_code:Locale_Code = "en_us")->None:
        super().__init__(value,locale_code=locale_code)
        self.currency_code = currency_code
        self._decimal_context = Context(
            prec=cur.CURRY_FORMATS[currency_code].decimals, 
            rounding = Currency_Attribute.rounding
        )

    @property
    def value(self)->Decimal:
        return Decimal(str(self._value).replace(",","."))
    @property
    def formatted_value(self)->str:
        return cur.CURRY_FORMATS[self.currency_code].present(str(self._value).replace(",","."),self._locale_code)

    @staticmethod
    def valid_entry(value:str) -> bool:
        if str(value).strip()=="": return True
        value = str(value).replace(",",".")
        try: return float(value)>0
        except: return False
    
    def copy(self)->Currency_Attribute:
        return Currency_Attribute(self.currency_code,self._value, locale_code=self._locale_code)
    
    def _set_currency(self,currency_code:cur.Currency_Code)->None:
        if currency_code not in cur.CURRY_FORMATS: 
            raise cur.UndefinedCurrency(
                f"Cannot set currency. Code {currency_code} is not defined."
            )
        else:
            self.currency_code = currency_code
            self.selected_choices["currency"] = currency_code


    def set(self,value:str="")->None:
        formatted_currency = cur.convert_to_currency(value)
        if formatted_currency != ():
            self._value = formatted_currency[0]
            self._set_currency(formatted_currency[1])

        elif self.valid_entry(value) and not str(value).strip()=="": 
            self._value = str(value)
    

class Date_Attr(_Attribute):
    default_value = datetime.date.today()

    def __init__(self, value:str|None=None, locale_code:Locale_Code = "en_us")->None:
        super().__init__(value,locale_code=locale_code)
        if value is not None and self.final_validation(value):
            self._value = dates.enter_date(value,dates.DATE_FORMATS[locale_code])
        else:
            self._value = self.default_value
        self._format = dates.DATE_FORMATS[self._locale_code]

    @property
    def value(self)->str: 
        return self._value
    @property
    def formatted_value(self)->str:
        return dates.date_to_str(self._value,dates.DATE_FORMATS[self._locale_code])
    
    @staticmethod
    def valid_entry(value:str)->bool: 
        if value.strip()=="": return True
        if re.fullmatch("[\d\._\- ]*",value): return True
        return False

    def final_validation(self, value:str)->bool:
        return dates.validate_date(value,dates.DATE_FORMATS[self._locale_code])
    
    def copy(self)->Date_Attr:
        return Date_Attr(self.value, locale_code=self._locale_code)
    
    def set(self,value:str="")->None:
        is_valid = self.final_validation(value)
        if is_valid and not str(value).strip()=="":
            self._value = dates.enter_date(value, dates.DATE_FORMATS[self._locale_code])


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
        return Name_Attr(self._value, locale_code=self._locale_code)
    

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
        return Text_Attr(self._value, locale_code=self._locale_code)
    


