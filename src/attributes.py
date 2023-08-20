from __future__ import annotations
from typing import Any

import abc
import re

import dates


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
        return Positive_Int_Attr(self.value)
    

import datetime, dates
class Date_Attr(_Attribute):
    default_value = datetime.date.today()
    date_formatter = dates.get_date_converter("%d.%m.%Y")

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
        return Date_Attr.date_formatter.validate_date(value)
    
    def copy(self)->Date_Attr:
        return Date_Attr(self.value)
    
    def set(self,value:str="")->None:
        if self.valid_entry(value) and not str(value).strip()=="":
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
        return Name_Attr(self.value)
    

class Text_Attr(_Attribute):
    default_value = "Text"
    @property
    def value(self)->str: return str(self._value)
    @staticmethod
    def valid_entry(value:str)->bool: return True

    def copy(self)->Text_Attr:
        return Text_Attr(self.value)
    

def create_attribute(value:Any)->_Attribute:
    if Positive_Int_Attr.valid_entry(value):
        return Positive_Int_Attr(value)
    elif Name_Attr.valid_entry(value):
        return Name_Attr(value)
    else:
        return Text_Attr(value)
