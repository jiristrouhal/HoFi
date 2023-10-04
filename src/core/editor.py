from __future__ import annotations


from typing import Tuple, Dict, List, Any, Optional
from src.core.item import ItemCreator, Item, Template, Attribute_Data_Constructor


import re

class Case_Template:
    def __init__(self)->None:
        self.__templates:Dict[str, Template] = {}
        self.__case_child_labels:List[str] = list()
        self.__attributes:Dict[str,Dict[str,Any]] = {}
        self.__constructor = Attribute_Data_Constructor()

    @property
    def attr(self)->Attribute_Data_Constructor: return self.__constructor
    @property
    def templates(self)->Dict[str,Template]: return self.__templates
    @property
    def case_child_labels(self)->Tuple[str,...]: return tuple(self.__case_child_labels)
    @property
    def attributes(self)->Dict[str,Dict[str,Any]]: return self.__attributes.copy()

    def add(
        self,
        label:str, 
        attribute_info:Dict[str,Dict[str,Any]], 
        child_template_labels:Optional[Tuple[str,...]] = None,
        dependencies:Optional[List[Template.Dependency]] = None
        )->None:

        label = label.strip()
        if label=='': raise Case_Template.BlankTemplateLabel
        
        if re.fullmatch('[\w]+',label) is None: 
            raise Case_Template.InvalidCharactersInLabel(
                f"Invalid label '{label}'. Only alphanumeric characters"
                 "(a-z, A-Z and 0-9) plus '_' are allowed.")

        for attr, info in attribute_info.items():
            if attr not in self.__attributes: self.__attributes[attr] = info
            elif info['atype'] != self.__attributes[attr]['atype']: 
                raise Case_Template.ReaddingAttributeWithDifferentType(
                    f"Attribute '{attr}' has type {info}. Previously was added with type '{self.__attributes[attr]}'."
                )

        self.__templates[label] = Template(label, attribute_info, child_template_labels, dependencies)


    def add_case_child_label(self,*labels:str)->None:
        for label in labels:
            if label not in self.__templates: raise Case_Template.UndefinedTemplate(label)
            self.__case_child_labels.append(label)


    class Dependency(Template.Dependency):
        pass

    class BlankTemplateLabel(Exception): pass
    class ReaddingAttributeWithDifferentType(Exception): pass
    class UndefinedTemplate(Exception): pass
    class InvalidCharactersInLabel(Exception): pass


from src.core.item import Attribute_Data_Constructor
class Editor:
    def __init__(self, case_template:Case_Template)->None:
        self.__creator = ItemCreator()
        for label, template in case_template.templates.items():
            self.__creator.add_template(label, template.attribute_info, template.child_itypes, template.dependencies)
        self.__creator.add_template('', {}, case_template.case_child_labels)
        self.__root = self.__creator.new("_")
        self.__attributes =  case_template.attributes

    @property
    def attributes(self)->Dict[str,Dict[str,Any]]: return self.__attributes

    def contains_case(self,case:Item)->bool:
        return self.__root.is_parent_of(case)

    from src.core.item import Parentage_Data
    def duplicate_as_case(self,item:Item)->Item:
        case = self.__creator.from_template("", item.name)
        item_dupl = item.copy()
        self.__root.controller.run(
            *self.__root.command['adopt'](self.Parentage_Data(self.__root, case)),
            *case.command['adopt'](self.Parentage_Data(case, item_dupl)),
        )
        return case

    def item_types_to_create(self,parent:Item)->Tuple[str,...]:
        types = self.__creator.template(parent.itype).child_itypes
        if types is None: return ()
        else: return types

    def new(self,parent:Item,itype:str)->Item:
        try:
            item = self.__creator.from_template(itype)
            parent.adopt(item)
        except Item.CannotAdoptItemOfType:
            raise Editor.InvalidChildTypeUnderGivenParent(
                f"Parent type: {parent.itype}, child type: {itype}."
            )
        except ItemCreator.UndefinedTemplate:
            raise Editor.UndefinedTemplate(itype)
        return item
    
    def new_case(self,name:str)->Item:
        case = self.__creator.from_template("",name)
        self.__root.adopt(case)
        return case

    def remove(self,item:Item,parent:Item)->None:
        if parent==item.parent: parent.leave(item)

    def remove_case(self,case:Item)->None:
        self.__root.leave(case)
    
    def undo(self)->None:
        self.__creator.undo()

    def redo(self)->None:
        self.__creator.redo()

    def value(self,item:Item,attribute_name:str,**options)->str:
        return item.attribute(attribute_name).print(**options)

    class InvalidChildTypeUnderGivenParent(Exception): pass
    class UndefinedTemplate(Exception): pass


def new_editor(case_template:Case_Template)->Editor:
    return Editor(case_template)


def blank_case_template()->Case_Template:
    return Case_Template()