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


class Case:
    def __init__(self,name:str, creator:ItemCreator, root:Item)->None:
        self.__creator = creator
        self.__item = self.__creator.new(name)
        root.adopt(self.__item)

    @property
    def name(self)->str: return self.__item.name
    @property
    def itype(self)->str: return ""

    def adopt(self,item:Item)->None: self.__item.adopt(item)
    def contains(self,item:Item)->bool: return self.__item.is_ancestor_of(item)
    def rename(self,name:str)->None: self.__item.rename(name)


class Editor:
    def __init__(self, case_template:Case_Template)->None:
        self.__creator = ItemCreator()
        for label, template in case_template.templates.items():
            self.__creator.add_template(label, template.attribute_info, template.child_itypes)
        self.__creator.add_template('', {}, case_template.case_child_labels)
        self.__root = self.__creator.new("_")

    def item_types_to_create(self,parent:Case|Item)->Tuple[str,...]:
        types = self.__creator.template(parent.itype).child_itypes
        if types is None: return ()
        else: return types

    def new(self,parent:Case|Item,itype:str)->Item:
        try:
            item = self.__creator.from_template(itype)
            parent.adopt(item)
        except:
            raise Editor.InvalidChildTypeUnderGivenParent(
                f"Parent type: {parent.itype}, child type: {itype}."
            )
        return item

    def new_case(self,name:str)->Case:
        return Case(name, self.__creator, self.__root)
    
    def undo(self)->None:
        self.__creator.undo()

    def redo(self)->None:
        self.__creator.redo()

    class InvalidChildTypeUnderGivenParent(Exception): pass


def new_editor(case_template:Case_Template)->Editor:
    return Editor(case_template)


def blank_case_template()->Case_Template:
    return Case_Template()