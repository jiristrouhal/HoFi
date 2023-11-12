from __future__ import annotations


from typing import Tuple, Dict, List, Any, Optional
from src.core.item import ItemCreator, Item, Template, Attribute_Data_Constructor 
from src.core.item import FileType, freeatt_child, freeatt, freeatt_parent
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
        self.__case_template:Optional[Template] = None

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
                    f"Attribute '{attr}' has type {info['atype']}. "
                    f"Previously was added with type '{self.__attributes[attr]}'."
                )

        self.__templates[label] = Template(label, attribute_info, child_template_labels, dependencies)

    def set_case_template(
        self, 
        attribute_info:Dict[str, Dict[str, Any]], 
        child_template_labels:Tuple[str,...], 
        dependencies:Optional[List[Template.Dependency]] = None
        )->None:

        self.add(CASE_TYPE_LABEL, attribute_info, child_template_labels, dependencies)

    def add_case_child_label(self,*labels:str)->None:
        for label in labels:
            if label not in self.__templates: raise Case_Template.UndefinedTemplate(label)
            self.__case_child_labels.append(label)

    def configure(self, **kwargs)->None:
        for label, value in kwargs.items():
            match label:
                case "currency_code": self.__currency = value
                case _: continue            

    def dependency(self, dependent:str, func:Callable[[Any],Any], *free:Template.Free_Attribute)->Case_Template.Dependency:
        return Case_Template.Dependency(dependent, func, free)

    def set_insertable(self,template_label:str)->None:
        if template_label not in self.__templates: raise Case_Template.UndefinedTemplate(template_label)
        self.__insertable = template_label

    def _list_templates(self)->Tuple[Template,...]:
        returned_templates = list(self.__templates.values())
        if not CASE_TYPE_LABEL in self.__templates:
            returned_templates.insert(0,Template(CASE_TYPE_LABEL, {}, tuple(self.__case_child_labels)))
        return returned_templates


    class Dependency(Template.Dependency): pass
    class BlankTemplateLabel(Exception): pass
    class ReaddingAttributeWithDifferentType(Exception): pass
    class UndefinedTemplate(Exception): pass
    class InvalidCharactersInLabel(Exception): pass


from src.core.item import Attribute_Data_Constructor
class Editor:
    def __init__(
        self, 
        case_template:Case_Template, 
        locale_code:Locale_Code, 
        lang:Optional[Lang_Object] = None,
        ignore_duplicit_names:bool = False
        )->None:

        self.__creator = ItemCreator(locale_code, case_template.currency_code,ignore_duplicit_names)
        self.__creator.add_templates(*case_template._list_templates())
        self.__root = self.__creator.new("_")
        self.__attributes =  case_template.attributes
        self.__insertable = case_template.insertable
        self.__locale_code = locale_code
        if lang is None: self.__lang = Lang_Object.get_lang_object()
        else: self.__lang = lang

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
    @property
    def export_dir_path(self)->str: return self.__creator.file_path
        
    def _cases(self)->Set[Item]: 
        return self.__root.children.copy()

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
        
        @self.__creator._controller.single_cmd()
        def load_and_adopt()->Item:
            item = self.__creator.load(dirpath, name, filetype)
            parent.adopt(item)
            return item
        return load_and_adopt()

    @staticmethod
    def is_case(item:Item)->bool:
        return item.itype==CASE_TYPE_LABEL

    def item_types_to_create(self,parent:Item)->Tuple[str,...]:
        return self.__creator.get_template(parent.itype).child_itypes

    def load_case(self,dirpath:str,name:str, ftype:FileType)->Item:
        @self.__creator._controller.single_cmd()
        def load_case_and_add_to_editor()->Item:
            case = self.__creator.load(dirpath, name, ftype)
            self.__root.adopt(case)
            return case
        return load_case_and_add_to_editor()

    def new(self,parent:Item,itype:str)->Item:
        if itype not in self.__creator.templates:
            raise Editor.UndefinedTemplate(itype)
        
        available_itypes = self.item_types_to_create(parent)
        if (available_itypes is None) or (itype not in available_itypes):
            raise Editor.InvalidChildTypeUnderGivenParent(
                f"Parent type: {parent.itype}, child type: {itype}."
            )
        
        @self.__creator._controller.single_cmd()
        def create_and_adopt()->Item:
            item = self.__creator.from_template(itype, name=self.__lang.label("Item_Types",itype))
            parent.adopt(item)
            return item
        return create_and_adopt()
    
    def new_case(self,name:str)->Item:
        @self.__creator._controller.single_cmd()
        def create_and_adopt()->Item:
            case = self.__creator.from_template(CASE_TYPE_LABEL, name=name)
            self.__root.adopt(case)
            return case
        return create_and_adopt()

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


def new_editor(
    case_template:Case_Template, 
    locale_code:Locale_Code="en_us", 
    lang:Optional[Lang_Object] = None,
    ignore_duplicit_names:bool = False
    )->Editor:

    return Editor(case_template, locale_code, lang, ignore_duplicit_names)


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
import os
class EditorUI(abc.ABC):

    def __init__(
        self, 
        editor:Editor,
        item_menu:Item_Menu,
        item_window:Item_Window,
        caseview:Case_View,
        lang:Optional[Lang_Object] = None
        )->None:

        self.__editor = editor
        self.__item_menu = item_menu
        self.__item_window = item_window
        self.__caseview = caseview
        self._compose()
        if lang is None: lang = Lang_Object.get_lang_object()
        self.__lang = lang

    @property
    def caseview(self)->Case_View: return self.__caseview
    @property
    def editor(self)->Editor: return self.__editor

    @abc.abstractmethod
    def _compose(self)->None: pass

    def configure(self, **kwargs)->None:
        self.__caseview.configure(**kwargs)
        self.__item_window.configure(**kwargs)

    def delete_item(self, item:Item, *args)->None:
        if item!=self.__editor.root: item.parent.leave(item)

    def open_item_menu(self, item:Item, *args)->None:
        if item.is_null(): 
            raise EditorUI.Opening_Item_Menu_For_Nonexistent_Item
        elif item==self.__editor.root:
            self.__item_menu.open(self.__root_item_actions(),*args)
        elif item.itype==CASE_TYPE_LABEL:
            self.__item_menu.open(self.__case_actions(item),*args)
        else:
            self.__item_menu.open(self.__item_actions(item),*args)

    def import_case_from_xml(self)->None:
        case_dir_path, case_name = self._get_xml_path()
        if case_name.strip()=="": return
        self.__editor.load_case(case_dir_path, case_name, "xml")
     
    def export_case_to_xml(self, case:Item)->None:
        dir_path = self._get_export_dir()
        if not os.path.isdir(dir_path): return 
        self.__editor.set_dir_path(dir_path)
        self.__editor.save(case, "xml")

    @abc.abstractmethod
    def _get_xml_path(self)->Tuple[str,str]:
        pass

    @abc.abstractmethod
    def _get_export_dir(self)->str: pass

    def __root_item_actions(self)->Item_Menu_Cmds:
        item_actions = Item_Menu_Cmds()
        item_actions.insert({'import_from_xml':self.import_case_from_xml})
        item_actions.insert({'new_case':self.__new_case})
        return item_actions
    
    def __case_actions(self, case:Item)->Item_Menu_Cmds:
        actions = Item_Menu_Cmds()
        for itype in self.__editor.item_types_to_create(case):
            actions.insert({itype: partial(self.__editor.new, case,itype)}, "add")
        actions.insert({'edit':lambda: self.open_item_window(case)})
        actions.insert({'export_to_xml': lambda: self.export_case_to_xml(case)})
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
        if item is not self.__editor.root:
            self.__item_window.open(item)
    
    def __new_case(self)->None:
        self.__editor.new_case(self.__lang.label("Item_Types","Case"))

    
    class Opening_Item_Menu_For_Nonexistent_Item(Exception): pass



from typing import Callable
from src.core.attributes import Attribute
import abc
class Item_Window(abc.ABC):

    def __init__(self, lang:Optional[Lang_Object] = None)->None:
        if lang is None: lang = Lang_Object_NULL()
        self.__lang = lang
        self.__open:bool = False


    @property
    def is_open(self)->bool: return self.__open
    @property
    def lang(self)->Lang_Object: return self.__lang

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
    def configure(self, **kwargs)->None:
        pass
        
    @abc.abstractmethod
    def _build_window(self, attributes:Dict[str,Attribute]): pass  # pragma: no cover
    @abc.abstractmethod
    def _destroy_window(self): pass  # pragma: no cover


class Item_Menu(abc.ABC):

    def __init__(self, lang:Lang_Object)->None:
        self.__actions:Optional[Item_Menu_Cmds] = None
        self.__open:bool = False
        self.__lang = lang

    @property
    def is_open(self)->bool: return self.__open
    @property
    def actions(self)->Optional[Item_Menu_Cmds]: return self.__actions
    @property
    def lang(self)->Lang_Object: return self.__lang

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
    
    @abc.abstractmethod
    def configure(self, **kwargs)->None:
        pass


import xml.etree.ElementTree as et
class Lang_Object(abc.ABC):
    def __init__(self, *args)->None:
        pass
    
    @abc.abstractmethod
    def label(self, *path:str)->str: 
        pass

    def __call__(self, *path:str)->str: return self.label(*path)

    @staticmethod
    def get_lang_object(xml_lang_file_path:Optional[str]=None)->Lang_Object:
        if xml_lang_file_path is None: return Lang_Object_NULL()
        else:  return Lang_Object_Impl(xml_lang_file_path)

    class Xml_Language_File_Does_Not_Exist(Exception): pass


class Lang_Object_NULL(Lang_Object):

    def __init__(self,*args)->None: pass
    def label(self, *path)->str: return path[-1]


class Lang_Object_Impl(Lang_Object):

    def __init__(self, xml_lang_file_path:str)->None:
        if not os.path.isfile(xml_lang_file_path): 
            raise Lang_Object.Xml_Language_File_Does_Not_Exist(xml_lang_file_path)
        self.__root:et.Element = et.parse(xml_lang_file_path).getroot()

    def label(self, *path:str)->str: 
        item = self.__root
        for p in path: 
            item = item.find(p)
            if item is None: return path[-1]
        try:
            return item.attrib["Text"]
        except: 
            return path[-1]

