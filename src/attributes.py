from typing import Any

import abc
import re


class _Attribute(abc.ABC):
    default_value = ""

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


class Name_Attr(_Attribute):
    default_value = "New"
    @property
    def value(self)->str: return str(self._value)
    @staticmethod
    def valid_entry(value:str)->bool: 
        if value=="": return True
        if re.fullmatch("[^\W\d].*",str(value)) is None: return False
        return True
    

class Text_Attr(_Attribute):
    default_value = "Text"
    @property
    def value(self)->str: return str(self._value)
    @staticmethod
    def valid_entry(value:str)->bool: return True
    

def create_attribute(value:Any)->_Attribute:
    if Positive_Int_Attr.valid_entry(value):
        return Positive_Int_Attr(value)
    elif Name_Attr.valid_entry(value):
        return Name_Attr(value)
    else:
        return Text_Attr(value)