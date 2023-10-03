from __future__ import annotations


from typing import Tuple, Dict, List
from src.core.item import ItemCreator, Item, Template


class Case_Template:
    def __init__(self)->None:
        self.__templates:Dict[str, Template] = {}
        self.__case_child_labels:List[str] = list()

    @property
    def templates(self)->Dict[str,Template]: return self.__templates
    @property
    def case_child_labels(self)->Tuple[str,...]: return tuple(self.__case_child_labels)

    def add_template(self,label:str, attribute_info:Dict[str,str], child_template_labels)->None:
        if label.strip()=='': raise Case_Template.BlankTemplateLabel
        self.__templates[label] = Template(label, attribute_info, child_template_labels)
    
    def add_case_child_label(self,label:str)->None:
        self.__case_child_labels.append(label)

    class BlankTemplateLabel(Exception): pass


class Editor:
    def __init__(self, case_template:Case_Template)->None:
        self.__creator = ItemCreator()
        for label, template in case_template.templates.items():
            self.__creator.add_template(label, template.attribute_info, template.child_itypes)
        self.__creator.add_template('', {}, case_template.case_child_labels)
        self.__root = self.__creator.new("_")

    def item_types_to_create(self,parent:Item)->Tuple[str,...]:
        types = self.__creator.template(parent.itype).child_itypes
        if types is None: return ()
        else: return types

    def new(self,parent:Item,itype:str)->Item:
        try:
            item = self.__creator.from_template(itype)
            parent.adopt(item)
        except:
            raise Editor.InvalidChildTypeUnderGivenParent(
                f"Parent type: {parent.itype}, child type: {itype}."
            )
        return item

    def new_case(self,name:str)->Item:
        case = self.__creator.from_template("",name)
        self.__root.adopt(case)
        return case
    
    def undo(self)->None:
        self.__creator.undo()

    def redo(self)->None:
        self.__creator.redo()

    class InvalidChildTypeUnderGivenParent(Exception): pass


def new_editor(case_template:Case_Template)->Editor:
    return Editor(case_template)


def blank_case_template()->Case_Template:
    return Case_Template()