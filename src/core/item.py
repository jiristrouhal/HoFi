from typing import Dict, Any, Literal
import typing
import abc


Attribute_Type = Literal['text','integer']
class Attribute:
    
    def __init__(self,atype:Attribute_Type='text')->None:
        if atype not in typing.get_args(Attribute_Type): raise self.InvalidAttributeType(atype)
        self.__type = atype
        self.__value = ""

    @property
    def type(self)->Attribute_Type: return self.__type
    @property
    def value(self)->Any: return self.__value

    def set(self,value:Any)->None: 
        if not self.is_valid(value): raise self.InvalidValueType
        self.__value=value

    def is_valid(self, value:Any)->bool: 
        if self.__type=='integer':
            try: 
                int(value+1)
                return True
            except: return False
        return True

    class InvalidAttributeType(Exception): pass
    class InvalidValueType(Exception): pass


class Item:
    
    def __init__(self,name:str,attributes:Dict[str,Attribute]={})->None:
        self.rename(name)
        self.__attributes = attributes

    @property
    def name(self)->str: return self.__name
    @property
    def attributes(self)->Dict[str,Any]: return self.__attributes

    def rename(self,name:str)->None:
        name = name.strip()
        self.__raise_if_name_is_blank(name)
        self.__name = name
    
    def __raise_if_name_is_blank(self,name:str)->None:
        if name=="": raise self.BlankName

    class BlankName(Exception): pass