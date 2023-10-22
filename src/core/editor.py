from __future__ import annotations


from typing import Tuple, Dict, List, Any, Optional
from src.core.item import ItemCreator, Item, Template, Attribute_Data_Constructor, FileType
from src.core.attributes import Locale_Code

import re


CASE_TYPE_LABEL = "__Case__"


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
    def currency_code(self)->Currency_Code: return self.__currency

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
            if attr not in self.__attributes: 
                self.__attributes[attr] = info
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
        self.__creator = ItemCreator(locale_code, case_template.currency_code)
        self.__creator.add_templates(*case_template.templates.values())
        self.__creator.add_template(CASE_TYPE_LABEL, {}, case_template.case_child_labels)
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
    @property
    def root(self)->Item: return self.__root
    @property
    def ncases(self)->int: return len(self.__root.children)

    def can_save_as_item(self,item:Item)->bool:
        return item.itype == self.__insertable

    def can_insert_under(self,parent:Item)->bool:
        parent_template = self.__creator.get_template(parent.itype)
        return self.__insertable in parent_template.child_itypes

    def contains_case(self,case:Item)->bool:
        return self.__root.is_parent_of(case)
    
    from src.core.item import Parentage_Data
    def duplicate_as_case(self,item:Item)->Item:
        case = self.__creator.from_template(CASE_TYPE_LABEL, item.name)
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
        return item.itype==CASE_TYPE_LABEL

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
        case = self.__creator.from_template(CASE_TYPE_LABEL,name)
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
            case = self.__creator.from_template(CASE_TYPE_LABEL, item.name)
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


from typing import Set
class Item_Menu_Cmds:
    
    def __init__(self, init_cmds:Dict[str,Callable[[],None]]={})->None:
        self.__items:Dict[str,Item_Menu_Cmds|Callable[[],None]] = dict()
        self.__children:Dict[str,Item_Menu_Cmds] = dict()
        self.__custom_cmds_after_menu_cmd:Set[Callable[[],None]] = set()

        self.insert(init_cmds)

    @property
    def items(self)->Dict[str,Item_Menu_Cmds|Callable[[],None]]: return self.__items.copy()

    def add_post_cmd(self, cmd:Callable[[],None])->None:
        self.__custom_cmds_after_menu_cmd.add(cmd)

    def cmd(self, label:str, *cmd_path:str)->Callable[[],None]:
        if cmd_path: 
            return self.__children[cmd_path[0]].cmd(label,*cmd_path[1:])
        else:
            cmd = self.__items[label]
            assert(callable(cmd))
            return cmd

    def insert(self, commands:Dict[str, Callable[[],None]], *cmd_path:str)->None:
        if not commands: return
        if cmd_path:
            if cmd_path[0] not in self.__children: 
                self.__children[cmd_path[0]] = Item_Menu_Cmds()
            self.__children[cmd_path[0]].insert(commands, *cmd_path[1:])
            self.__items[cmd_path[0]] = self.__children[cmd_path[0]]
        else:
            self.__items.update(commands.copy())

    def labels(self, *cmd_path:str)->List[str]: 
        if cmd_path: 
            if cmd_path[0] not in self.__children: return []
            return self.__children[cmd_path[0]].labels(*cmd_path[1:])
        else:
            return list(self.__items.keys())

    def run(self, label, *cmd_path)->None:
        self.cmd(label,*cmd_path)()
        for cmd in self.__custom_cmds_after_menu_cmd: cmd()


import abc
from functools import partial
class EditorUI(abc.ABC):

    def __init__(
        self, 
        editor:Editor,
        item_menu:Item_Menu,
        item_window:Item_Window,
        caseview:Case_View
        )->None:

        self.__editor = editor
        self.__item_menu = item_menu
        self.__item_window = item_window
        self.__caseview = caseview
        self._compose()

    @property
    def caseview(self)->Case_View: return self.__caseview
    @property
    def editor(self)->Editor: return self.__editor

    @abc.abstractmethod
    def _compose(self)->None: pass

    def open_item_menu(self, item:Item, *args)->None:
        if item.is_null(): 
            raise EditorUI.Opening_Item_Menu_For_Nonexistent_Item
        elif item==self.__editor.root:
            self.__item_menu.open(self.__root_item_actions(),*args)
        elif item.itype==CASE_TYPE_LABEL:
            self.__item_menu.open(self.__case_actions(item),*args)
        else:
            self.__item_menu.open(self.__item_actions(item),*args)

    def __root_item_actions(self)->Item_Menu_Cmds:
        item_actions = Item_Menu_Cmds()
        item_actions.insert({'new_case':self.__new_case})
        return item_actions
    
    def __case_actions(self, case:Item)->Item_Menu_Cmds:
        actions = Item_Menu_Cmds()
        for itype in self.__editor.item_types_to_create(case):
            actions.insert({itype: partial(self.__editor.new, case,itype)}, "add")
        actions.insert({'edit':lambda: self.open_item_window(case)})
        actions.insert({'delete':lambda: self.__editor.remove_case(case)})
        return actions

    def __item_actions(self, item:Item)->Item_Menu_Cmds:
        actions = Item_Menu_Cmds()
        for itype in self.__editor.item_types_to_create(item):
            actions.insert({itype: partial(self.__editor.new, item ,itype)}, "add")
        actions.insert({'edit':lambda: self.open_item_window(item)})
        actions.insert({'delete':lambda: self.__editor.remove(item, item.parent)})
        return actions
    
    def open_item_window(self, item:Item, *args)->None:
        self.__item_window.open(item)
    
    DEFAULT_CASE_NAME = "Case"
    def __new_case(self)->None:
        self.__editor.new_case(EditorUI.DEFAULT_CASE_NAME)

    
    class Opening_Item_Menu_For_Nonexistent_Item(Exception): pass



from typing import Callable
from src.core.attributes import Attribute
import abc
class Item_Window(abc.ABC):

    def __init__(self)->None:
        self.__open:bool = False

    @property
    def is_open(self)->bool: return self.__open

    def open(self, item:Item)->None: 
        name_attr = item._manager._attrfac.new("name",item.name)
        rename_action = lambda: item._rename(name_attr.value)

        name_attr.add_action_on_set("item_window", rename_action)
        attributes:Dict[str,Attribute] = {"name":name_attr}
        attributes.update(item.attributes)
        self._build_window(attributes)
        self.__open = True

    def close(self)->None:
        self._destroy_window()
        self.__open = False
        
    @abc.abstractmethod
    def _build_window(self, attributes:Dict[str,Attribute]): pass  # pragma: no cover
    @abc.abstractmethod
    def _destroy_window(self): pass  # pragma: no cover


class Item_Menu(abc.ABC):

    def __init__(self)->None:
        self.__actions:Optional[Item_Menu_Cmds] = None
        self.__open:bool = False

    @property
    def is_open(self)->bool: return self.__open
    @property
    def actions(self)->Optional[Item_Menu_Cmds]: return self.__actions

    def action_labels(self, *cmd_path)->List[str]: 
        if self.__actions is not None:
            return self.__actions.labels(*cmd_path)
        else: 
            return []

    def close(self)->None: 
        self.__open = False
        self._destroy_menu()
        self.__actions = None

    def open(self, actions:Item_Menu_Cmds, *args)->None: 
        if not actions.labels(): 
            return 
        else:
            self.__actions = actions
            self.__open = True
            self._build_menu(*args)
            self.__actions.add_post_cmd(self.close)

    def run(self, action_label:str, *cmd_path:str)->None:
        if self.__actions is not None:
            self.__actions.run(action_label,*cmd_path)

    @abc.abstractmethod
    def _build_menu(self,*args)->None: pass # pragma: no cover
    @abc.abstractmethod
    def _destroy_menu(self)->None: pass # pragma: no cover
    

class Case_View(abc.ABC):
    pass
