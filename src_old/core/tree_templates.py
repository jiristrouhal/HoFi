from __future__ import annotations

from typing import Dict, Tuple, List, Any, Set, OrderedDict, Callable
import dataclasses
from functools import partial
from re import match

import src.core.attributes as attrs
from src.lang.lang import Locale_Code


class TemplateLocked(Exception): pass


@dataclasses.dataclass(frozen=True)
class User_Defined_Command:
    label:str
    condition:Callable[[Any],bool]
    command:Callable[[Any],None]


class AppTemplate:

    def __init__(self, locale_code:Locale_Code="en_us", name_attr:str="name")->None:
        self.__locale_code = locale_code
        if name_attr.strip()=="":  name_attr="name"
        self.__name_attr = name_attr
        self.__templates:Dict[str, Template] = dict()
        self.__attribute_factory = attrs.Attribute_Factory(locale_code)

    @property
    def locale_code(self)->Locale_Code: return self.__locale_code
    @property
    def name_attr(self)->str: return self.__name_attr
    
    def add(self,*templates:NewTemplate)->None:
        self.__detect_missing_child_templates(*templates)
        self.__add_templates(templates)
    

    def remove(self,tag:str)->None:
        if not self.__template_exists(tag): 
            raise KeyError(f"Template with tag '{tag}' was not defined.")
        self.__raise_if_template_is_child_of_another(tag)
        if self.__templates[tag]._locked:
            raise TemplateLocked(f"Cannot delete locked template '{tag}'.")
        self.__templates.pop(tag)

    def __call__(self, tag:str)->Template:
        return self.template(tag)

    def template(self,tag:str)->Template:
        if not self.__template_exists(tag): raise KeyError(f"Template with tag '{tag}' was not defined.")
        return self.__templates[tag]

    def _modify_template(
        self,
        tag:str,
        new_attributes:OrderedDict[str,Any]=OrderedDict(),
        new_children:Tuple[str,...]|None=None
        )->None:

        if not self. __template_exists(tag):
            raise KeyError(f"Cannot modify template '{tag}'. No such template is defined.")

        if self.__templates[tag]._locked:
            raise TemplateLocked(f"Cannot modify locked template '{tag}'.")

        if new_attributes:
            self.__check_attributes_contain_name(tag,new_attributes)
            self.__templates[tag]._attributes = self.__create_attributes(new_attributes)
        if new_children is not None:
            self.__detect_missing_child_templates(NewTemplate(tag,new_attributes,new_children))
            self.__templates[tag]._children = new_children


    def template_tags(self)->List[str]: 
        return list(self.__templates.keys())

    def clear(self)->None:
        self.__templates.clear()

    @staticmethod
    def __check_attributes_contain_name(tag:str,attributes:OrderedDict[str,Any])->None:
        if "name" not in attributes: raise KeyError(
            f"The 'name' attribute is missing in the '{tag} template (re)definition."
        )

    def __add_templates(self,templates:Tuple[NewTemplate,...])->None:
        for t in templates:
            if self.__template_exists(t.tag): 
                raise KeyError(f"Template with tag {t.tag} already exists.")
            
            dependent_attributes:OrderedDict[str,Callable] = OrderedDict()
            for attr_name, value in t.attributes.items():
                if callable(value): 
                    dependent_attributes[attr_name] = value
            for attr_name in dependent_attributes:
                t.attributes.pop(attr_name)

            attributes = {self.__name_attr:t.tag}
            attributes.update(t.attributes)
            self.__templates[t.tag] = Template(
                _attributes = self.__create_attributes(OrderedDict(attributes)),
                _dependent_attributes = self.__create_attributes(dependent_attributes),
                _children=t.children,
                _locked=t.locked,
                _icon_file=t.icon_file,
                _user_def_cmds=t.user_def_cmds,
                variable_defaults=t.variable_defaults
            )

    def __detect_missing_child_templates(self,*to_be_added:NewTemplate)->None:
        available_templates = set([t.tag for t in to_be_added] + self.template_tags())
        required_templates:Set[str] = set()
        for template in to_be_added: 
            for child in template.children: required_templates.add(child)
        if not required_templates.issubset(available_templates):
            raise KeyError(
                "New templates misses definition of the following child templates: "\
                f"{required_templates-available_templates}"
            )
    
    def __raise_if_template_is_child_of_another(self,tag:str)->None:
        other_tags = self.template_tags()
        other_tags.remove(tag)
        for other_tag in other_tags:
            if tag in self.__templates[other_tag].children: 
                raise Exception(
                    f"Cannot remove template '{tag}'. It is used as a child by '{other_tag}'."
                )
        
    def __create_attributes(self, new_attributes:OrderedDict[str,Any])->OrderedDict[str,Any]:
        attributes = OrderedDict()
        for name, value in new_attributes.items():
            if isinstance(value,tuple):
                attributes[name] = self.__attribute_factory.create_attribute(value[1],value[0])
            else:
                attributes[name] = self.__attribute_factory.create_attribute(value)
        return attributes

    def __template_exists(self,tag:str)->bool:
        return tag in self.__templates



@dataclasses.dataclass(frozen=True)
class NewTemplate:
    tag:str
    attributes:Dict[str,Any]
    children:Tuple[str,...]
    locked:bool = False
    icon_file:Any = None # relative path to a widget icon
    user_def_cmds:List[User_Defined_Command] = \
        dataclasses.field(default_factory=list)
    variable_defaults:Dict[str,Callable[[Any],Any]] = \
        dataclasses.field(default_factory=OrderedDict)
    
    def __post_init__(self)->None:
        if match("[^\w]",self.tag.strip()) is not None: 
            raise KeyError(f"Invalid template tag '{self.tag}'. "
                           f"The tag must constist only of alpha-numeric "
                            "characters (a-z, A-Z, 0-9) and the underscore '_'")
        for key in self.variable_defaults:
            if key not in self.attributes: 
                raise KeyError(
                    f"Cannot set default value. \n"
                    f"The attribute '{key}' is not defined in the template '{self.tag}'.")


@dataclasses.dataclass
class Template:
    _attributes:OrderedDict[str,attrs._Attribute]
    _dependent_attributes:OrderedDict[str,attrs.Dependent_Attr]
    _children:Tuple[str,...]
    _locked:bool
    _icon_file:Any
    _user_def_cmds:List[User_Defined_Command] = \
        dataclasses.field(default_factory=list)
    variable_defaults:Dict[str,Callable[[Any],Any]] = \
        dataclasses.field(default_factory=OrderedDict)

    @property
    def locked(self)->bool: return self._locked

    @property
    def icon_file(self)->Any: return self._icon_file

    @property
    def attributes(self)->OrderedDict[str,attrs._Attribute]:
        instance_attributes = OrderedDict()
        for name, attr in self._attributes.items():
            instance_attributes[name] = attr.copy()
        return instance_attributes

    @property
    def dependent_attributes(self)->OrderedDict[str,attrs.Dependent_Attr]:
        instance_attributes = OrderedDict()
        for name, attr in self._dependent_attributes.items():
            instance_attributes[name] = attr.copy()
        return instance_attributes
    
    def user_defined_commands(self,obj:attrs.AttributesOwner)->List[User_Defined_Command]:
        return self._user_def_cmds
    
    @property
    def children(self)->Tuple[str,...]: 
        return tuple([c for c in self._children])
