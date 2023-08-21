from __future__ import annotations
from typing import Any, Tuple, Callable, Protocol, Dict

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

    @property
    def value(self)->Any: pass

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
    @staticmethod
    def valid_entry(value: str)->bool: return True

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
    @staticmethod
    def valid_entry(value:str)->bool: 
        if value=="": return True
        if re.fullmatch("\d+",str(value)) is None: return False
        return int(value)>0
    
    def copy(self)->Positive_Int_Attr:
        return Positive_Int_Attr(self._value)
    

import datetime, core.dates
class Date_Attr(_Attribute):
    default_value = datetime.date.today()
    date_formatter = core.dates.get_date_converter("%d.%m.%Y")

    def __init__(self, value:str|None=None)->None:
        if value is None or not self.valid_entry(value): 
            self._value = self.default_value
        else:
            self._value = self.date_formatter.enter_date(value)
    @property
    def value(self)->str: 
        return self.date_formatter.print_date(self._value)
    
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
    @staticmethod
    def valid_entry(value:str)->bool: return True

    def copy(self)->Text_Attr:
        return Text_Attr(self._value)
    


def create_attribute(value:Any)->_Attribute:
    if callable(value):
        return Dependent_Attr(value)
    elif Positive_Int_Attr.valid_entry(value):
        return Positive_Int_Attr(value)
    elif Date_Attr.valid_entry(value):
        return Date_Attr(value)
    elif Name_Attr.valid_entry(value):
        return Name_Attr(value)
    else:
        return Text_Attr(value)
