import datetime
from typing import Any, Dict
from src.core.attributes import Attribute_Data_Constructor


class Timeline_Template:
    def __init__(self)->None:
        self.__attrc = Attribute_Data_Constructor()
        self.__vars:Dict[str,Dict[str,Any]] = dict()

    @property
    def attr(self)->Attribute_Data_Constructor: return self.__attrc
    @property
    def vars(self)->Dict[str,Dict[str,Any]]: return self.__vars.copy()

    def addvar(self,label:str,info:Dict[str,Any])->None:
        if label in self.__vars: raise Timeline_Template.VariableAlreadyDefined(label)
        else: self.__vars[label] = info

    class VariableAlreadyDefined(Exception): pass


class Timeline:

    def __init__(self, template:Timeline_Template)->None:
        self.__vars_info = template.vars
    
    def __call__(self, var_name:str, date:datetime.date)->Any:
        if var_name not in self.__vars_info: raise Timeline.UndefinedVariable(var_name)
        return self.__vars_info[var_name]['init_value']
    
    def add_day(self, date:datetime.date)->None:
        pass

    def has_var(self,var_name:str)->bool:
        return var_name in self.__vars_info
    
    def set_init(self,var_name:str, value:Any)->None:
        self.__vars_info[var_name]['init_value'] = value
    
    class UndefinedVariable(Exception): pass


def create_timeline(template:Timeline_Template)->Timeline:
    return Timeline(template)


def blank_timeline_template()->Timeline_Template:
    return Timeline_Template()