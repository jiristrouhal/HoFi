from __future__ import annotations


from typing import Tuple, Dict, List, Any, Optional
from src.core.item import ItemCreator, Item, Template, Attribute_Data_Constructor, FileType
from src.core.attributes import Locale_Code


import re


CASE_TEMPLATE_LABEL = "__Case__"


from src.core.attributes import Currency_Code
class Case_Template:
    def __init__(self)->None:
        self.__templates:Dict[str, Template] = {}
        self.__case_child_labels:List[str] = list()
        self.__attributes:Dict[str,Dict[str,Any]] = {}
        self.__constructor = Attribute_Data_Constructor()
        self.__insertable:str = ""
        self.__currency:Currency_Code = "USD"

    @property
    def attr(self)->Attribute_Data_Constructor: return self.__constructor
    @property
    def templates(self)->Dict[str,Template]: return self.__templates
    @property
    def case_child_labels(self)->Tuple[str,...]: return tuple(self.__case_child_labels)
    @property
    def attributes(self)->Dict[str,Dict[str,Any]]: return self.__attributes.copy()
    @property
    def insertable(self)->str: return self.__insertable
    @property
    def currency(self)->Currency_Code: return self.__currency

    def add(
        self,
        label:str, 
        attribute_info:Dict[str,Dict[str,Any]], 
        child_template_labels:Tuple[str,...] = (),
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

    def set_insertable(self,template_label:str)->None:
        if template_label not in self.__templates: raise Case_Template.UndefinedTemplate(template_label)
        self.__insertable = template_label


    class Dependency(Template.Dependency): pass
    class BlankTemplateLabel(Exception): pass
    class ReaddingAttributeWithDifferentType(Exception): pass
    class UndefinedTemplate(Exception): pass
    class InvalidCharactersInLabel(Exception): pass


from src.core.item import Attribute_Data_Constructor
class Editor:
    def __init__(self, case_template:Case_Template, locale_code:Locale_Code)->None:
        self.__creator = ItemCreator(locale_code)
        self.__creator.add_templates(*case_template.templates.values())
        self.__creator.add_template(CASE_TEMPLATE_LABEL, {}, case_template.case_child_labels)
        self.__root = self.__creator.new("_")
        self.__attributes =  case_template.attributes
        self.__insertable = case_template.insertable
        self.__locale_code = locale_code

    @property
    def attributes(self)->Dict[str,Dict[str,Any]]: return self.__attributes
    @property
    def insertable(self)->str: return self.__insertable
    @property
    def locale_code(self)->Locale_Code: return self.__locale_code

    def can_save_as_item(self,item:Item)->bool:
        return item.itype == self.__insertable

    def can_insert_under(self,parent:Item)->bool:
        parent_template = self.__creator.get_template(parent.itype)
        return self.__insertable in parent_template.child_itypes

    def contains_case(self,case:Item)->bool:
        return self.__root.is_parent_of(case)
    
    from src.core.item import Parentage_Data
    def duplicate_as_case(self,item:Item)->Item:
        case = self.__creator.from_template(CASE_TEMPLATE_LABEL, item.name)
        item_dupl = item.copy()
        self.__root.controller.run(
            *self.__root.command['adopt'](self.Parentage_Data(self.__root, case)),
            *case.command['adopt'](self.Parentage_Data(case, item_dupl)),
        )
        return case

    def insert_from_file(self, parent:Item, dirpath:str, name:str, filetype:FileType)->Item:
        if not self.can_insert_under(parent):
            raise Editor.CannotInsertItemUnderSelectedParent(parent.name, parent.itype)
        item = self.__creator.load(dirpath, name, filetype)
        parent.adopt(item)
        return item

    @staticmethod
    def is_case(item:Item)->bool:
        return item.itype==CASE_TEMPLATE_LABEL

    def item_types_to_create(self,parent:Item)->Tuple[str,...]:
        return self.__creator.get_template(parent.itype).child_itypes

    def load_case(self,dirpath:str,case_name:str,filetype:FileType)->Item:
        case = self.__creator.load(dirpath, case_name, filetype)
        self.__root.adopt(case)
        return case

    def new(self,parent:Item,itype:str)->Item:
        if itype not in self.__creator.templates:
            raise Editor.UndefinedTemplate(itype)
        
        available_itypes = self.item_types_to_create(parent)
        if (available_itypes is None) or (itype not in available_itypes):
            raise Editor.InvalidChildTypeUnderGivenParent(
                f"Parent type: {parent.itype}, child type: {itype}."
            )
        item = self.__creator.from_template(itype)
        parent.adopt(item)
        return item
    
    def new_case(self,name:str)->Item:
        case = self.__creator.from_template(CASE_TEMPLATE_LABEL,name)
        self.__root.adopt(case)
        return case

    def remove(self,item:Item,parent:Item)->None:
        if parent==item.parent: parent.leave(item)

    def remove_case(self,case:Item)->None:
        self.__root.leave(case)

    def save(self,item:Item,filetype:FileType)->None:
        if Editor.is_case(item) or self.can_save_as_item(item):
            self.__creator.save(item,filetype)
        else:
            raise Editor.CannotSaveAsItem(item.name, item.itype)

    def save_as_case(self,item:Item,filetype:FileType)->None:
        if not Editor.is_case(item):
            case = self.__creator.from_template(CASE_TEMPLATE_LABEL, item.name)
            case.adopt_formally(item)
            self.__creator.save(case,filetype)
        else:
            self.__creator.save(item,filetype)

    def set_dir_path(self,dirpath:str)->None:
        self.__creator.set_dir_path(dirpath)
    
    def undo(self)->None:
        self.__creator.undo()

    def redo(self)->None:
        self.__creator.redo()

    def print(self,item:Item,attribute_name:str,**options)->str:
        return item.attribute(attribute_name).print(**options)

    class CannotExportCaseAsItem(Exception): pass
    class CannotInsertItemUnderSelectedParent(Exception): pass
    class CannotSaveAsItem(Exception): pass
    class InvalidChildTypeUnderGivenParent(Exception): pass
    class UndefinedTemplate(ItemCreator.UndefinedTemplate): pass


def new_editor(case_template:Case_Template, locale_code:Locale_Code="en_us")->Editor:
    return Editor(case_template, locale_code)


def blank_case_template()->Case_Template:
    return Case_Template()


from typing import Literal, Callable
class EditorUI:
    EditorLocation = Literal['tree']

    def __init__(self, editor:Editor)->None:
        self.__editor = editor
        self.__action_menu = Action_Menu()
        self.__item_window = Item_Window()
        self.__planner = Planner()

    @property
    def action_menu(self)->Action_Menu: return self.__action_menu
    @property
    def command_running(self)->bool: return False
    @property
    def item_window(self)->Item_Window: return self.__item_window
    @property
    def planner(self)->Planner: return self.__planner
    @property
    def selected_items(self)->List[Item]: return list()

    def open_action_menu(self, commands:Dict[str,Callable[[],None]])->None:
        self.__action_menu.open(commands)

    def open_item_window(self, item:Item)->None:
        if self.__action_menu.is_open: raise EditorUI.ActionMenuOpened
        self.__item_window.open(item)

    def open_planner(self)->None:
        if self.__action_menu.is_open: raise EditorUI.ActionMenuOpened


    class ActionMenuOpened(Exception): pass



import dataclasses
@dataclasses.dataclass(frozen=True)
class Item_Attribute:
    orig_value:Any
    validation_func:Callable[[Any],bool]
    set_func:Callable[[Any],None]
    options:Dict[str,Tuple[Any,...]] = dataclasses.field(default_factory=dict)




class Item_Window:

    def __init__(self)->None:
        self.__item:Optional[Item] = None
        self.__attributes:Dict[str, Item_Attribute] = {}

    @property
    def is_open(self)->bool: return self.__item is not None

    @property
    def attributes(self)->Dict[str, Item_Attribute]: return self.__attributes.copy()
    
    def open(self, item:Item)->None:
        self.__item = item
        for label, attr in self.__item.attributes.items():
            self.__attributes[label] = Item_Attribute(
                orig_value = attr.value, 
                validation_func = attr.is_valid, 
                set_func = attr.set
            )

    def close(self)->None:
        self.__item = None


class Action_Menu:
    def __init__(self)->None:
        self.__commands:Dict[str,Callable[[],None]] = {}

    @property
    def is_open(self)->bool: return bool(self.__commands)

    def open(self, commands:Dict[str,Callable[[],None]])->None: 
        if not commands: raise Action_Menu.NoCommands
        self.__commands = commands.copy()

    def run(self, command_label:str)->None: 
        if command_label not in self.__commands: raise Action_Menu.UndefinedCommand(command_label)
        self.__commands[command_label]()
        self.__commands.clear()

    class NoCommands(Exception): pass
    class UndefinedCommand(Exception): pass


class Planner:
    @property
    def is_open(self)->bool: return False

    def open(self)->None: pass