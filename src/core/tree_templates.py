import core.attributes as attrs
from typing import Dict, Tuple, List, Any, Set, OrderedDict, Callable
import dataclasses
import os

class TemplateLocked(Exception): pass

@dataclasses.dataclass(frozen=True)
class NewTemplate:
    tag:str
    attributes:OrderedDict[str,Any]
    children:Tuple[str,...]
    locked:bool = False
    icon_file:str|None = None # relative path to a widget icon

    def __post_init__(self)->None:
        if self.icon_file is not None and not os.path.isfile(self.icon_file):
            raise ValueError(f"The file '{self.icon_file}' was not found.")


@dataclasses.dataclass
class Template:
    _attributes:OrderedDict[str,attrs._Attribute]
    _dependent_attributes:OrderedDict[str,attrs.Dependent_Attr]
    _children:Tuple[str,...]
    _locked:bool
    _icon_file:str|None = None

    @property
    def locked(self)->bool: return self._locked

    @property
    def icon_file(self)->str|None: return self._icon_file

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
    
    @property
    def children(self)->Tuple[str,...]: 
        return tuple([c for c in self._children])


__templates:Dict[str, Template] = dict()



def add(*templates:NewTemplate)->None:
    __detect_missing_child_templates(*templates)
    __add_templates(templates)
    

def remove(tag:str)->None:
    if not __template_exists(tag): raise KeyError(f"Template with tag '{tag}' was not defined.")
    __raise_if_template_is_child_of_another(tag)
    if __templates[tag]._locked:
        raise TemplateLocked(f"Cannot delete locked template '{tag}'.")
    __templates.pop(tag)

def template(tag:str)->Template:
    if not __template_exists(tag): raise KeyError(f"Template with tag '{tag}' was not defined.")
    return __templates[tag]

def _modify_template(
    tag:str,
    new_attributes:OrderedDict[str,Any]=OrderedDict(),
    new_children:Tuple[str,...]|None=None
    )->None:

    if not __template_exists(tag):
        raise KeyError(f"Cannot modify template '{tag}'. No such template is defined.")

    if __templates[tag]._locked:
        raise TemplateLocked(f"Cannot modify locked template '{tag}'.")

    if new_attributes:
        __check_attributes_contain_name(tag,new_attributes)
        __templates[tag]._attributes = __create_attributes(new_attributes)
    if new_children is not None:
        __detect_missing_child_templates(NewTemplate(tag,new_attributes,new_children))
        __templates[tag]._children = new_children


def template_tags()->List[str]: return list(__templates.keys())

def clear()->None:
    __templates.clear()


def __check_attributes_contain_name(tag:str,attributes:OrderedDict[str,Any])->None:
    if "name" not in attributes: raise KeyError(
        f"The 'name' attribute is missing in the '{tag} template (re)definition."
    )

def __add_templates(templates:Tuple[NewTemplate,...])->None:
    for t in templates:
        if __template_exists(t.tag): 
            raise KeyError(f"Template with tag {t.tag} already exists.")
        
        dependent_attributes:OrderedDict[str,Callable] = OrderedDict()
        for attr_name, value in t.attributes.items():
            if callable(value): 
                dependent_attributes[attr_name] = value
        for attr_name in dependent_attributes:
            t.attributes.pop(attr_name)

        __templates[t.tag] = Template(
            _attributes = __create_attributes(t.attributes),
            _dependent_attributes = __create_attributes(dependent_attributes),
            _children=t.children,
            _locked=t.locked,
            _icon_file=t.icon_file
        )

def __detect_missing_child_templates(*to_be_added:NewTemplate)->None:
    available_templates = set([t.tag for t in to_be_added] + template_tags())
    required_templates:Set[str] = set()
    for template in to_be_added: 
        for child in template.children: required_templates.add(child)
    if not required_templates.issubset(available_templates):
        raise KeyError(
            "New templates misses definition of the following child templates: "\
            f"{required_templates-available_templates}"
        )
    
def __raise_if_template_is_child_of_another(tag:str)->None:
    other_tags = template_tags()
    other_tags.remove(tag)
    for other_tag in other_tags:
        if tag in __templates[other_tag].children: 
            raise Exception(
                f"Cannot remove template '{tag}'. It is used as a child by '{other_tag}'."
            )
        
def __create_attributes(new_attributes:OrderedDict[str,Any])->OrderedDict[str,attrs._Attribute]:
    attributes = OrderedDict()
    for name, value in new_attributes.items():
        attributes[name] = attrs.create_attribute(value)
    return attributes

def __template_exists(tag:str)->bool:
    return tag in __templates