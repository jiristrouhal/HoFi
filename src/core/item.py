from typing import Dict, Protocol, Any


class Attribute(Protocol):

    @property
    def value(self)->Any: ...


class Item:
    
    def __init__(self,name:str,attributes:Dict[str,Attribute]={})->None:
        self.rename(name)
        self.__attributes = attributes

    @property
    def name(self)->str: return self.__name
    @property
    def attributes(self)->Dict[str,Attribute]: 
        return self.__attributes
    @property
    def attribute_values(self)->Dict[str,Any]: 
        return {key:attr.value for key,attr in self.__attributes.items()}

    def rename(self,name:str)->None:
        name = name.strip()
        self.__raise_if_name_is_blank(name)
        self.__name = name
    
    def __raise_if_name_is_blank(self,name:str)->None:
        if name=="": raise self.BlankName


    class BlankName(Exception): pass