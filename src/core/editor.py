from __future__ import annotations


from typing import Tuple, Dict, List, Any, Optional, Callable, Literal
from src.core.item import ItemCreator, Item, Template, Attribute_Data_Constructor 
from src.core.item import FileType, freeatt_child, freeatt, freeatt_parent
from src.core.attributes import Locale_Code
from src.core.item import ItemImpl

import re


CASE_TYPE_LABEL = "__Case__"


from decimal import Decimal
MergeRule = Literal["sum", "join_texts", "max"]
_MergeFunc = Callable[[List[Any]], Any]


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
        self.__merge_rules:Dict[str, Dict[str, _MergeFunc]] = dict()

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
    @property
    def merging_rules(self)->Dict[str, Dict[str, _MergeFunc]]: return self.__merge_rules.copy()

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

    def add_merging_rule(self, itype:str, attribute_rules:Dict[str, MergeRule])->None:
        if not itype in self.__templates: 
            raise Case_Template.Adding_Merge_Rule_To_Undefined_Item_Type(itype)
        elif itype in self.__merge_rules: 
            raise Case_Template.Merge_Rule_Already_Defined(itype)
        # create empty dict for merging rules of item type 'itype'
        self.__merge_rules[itype] = dict()
        # collect attribute labels for item type 'itype'
        attr_labels = self.__templates[itype].attribute_info.keys()
        # pick available merge rule from a dictionary of this class and assign it
        # to the attribute label 'alabel'
        for alabel in attr_labels:
            if alabel not in attribute_rules: 
                raise Case_Template.Attribute_With_Undefined_Merge_Rule(alabel)
            rule_label = attribute_rules[alabel]
            if rule_label not in self.__merge_func:
                raise Case_Template.Undefined_Merge_Function(rule_label)
            self.__merge_rules[itype][alabel] = self.__merge_func[rule_label]
 
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
    
    __merge_func:Dict[MergeRule, _MergeFunc] = {
        "sum": lambda x: sum(Decimal(str(xi)) for xi in x),
        "max": lambda x: max(x),
        "min": lambda x: min(x),
        "join_texts": lambda d: "\n\n".join(d)
    }

    class Adding_Merge_Rule_To_Undefined_Item_Type(Exception): pass
    class Attribute_With_Undefined_Merge_Rule(Exception): pass
    class BlankTemplateLabel(Exception): pass
    class Dependency(Template.Dependency): pass
    class InvalidCharactersInLabel(Exception): pass
    class Merge_Rule_Already_Defined(Exception): pass
    class ReaddingAttributeWithDifferentType(Exception): pass
    class Undefined_Merge_Function(Exception): pass
    class UndefinedTemplate(Exception): pass


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
        self.__root = self.__creator.new("_", child_itypes=(CASE_TYPE_LABEL,))
        self.__attributes =  case_template.attributes
        self.__insertable = case_template.insertable
        self.__locale_code = locale_code
        if lang is None: self.__lang = Lang_Object.get_lang_object()
        else: self.__lang = lang

        self.__copied_item:Optional[Item] = None

        self.__selection:Set[Item] = set()
        self.__actions_on_selection:Dict[str, List[Callable[[], None]]] = dict()

        self.__merging_rules:Dict[str, Dict[str, _MergeFunc]] = case_template.merging_rules

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
    @property
    def creator(self)->ItemCreator: return self.__creator
    @property
    def item_to_paste(self)->Item: return self.__copied_item
    @property
    def selection(self)->Set[Item]: return self.__selection
    @property
    def selection_is_mergeable(self)->bool:return self.is_mergeable(self.__selection)
    @property
    def selection_is_groupable(self)->bool: return self.is_groupable(self.__selection)

    def add_action_on_selection(self, owner_id:str, action:Callable[[], None])->None:
        if owner_id not in self.__actions_on_selection:
            self.__actions_on_selection[owner_id] = list()
        self.__actions_on_selection[owner_id].append(action)
    
    def can_paste_under_or_next_to(self, to_be_pasted:Item, other_item:Item)->bool: 
        if self.__copied_item is None:
            return False
        can_paste_under = other_item._can_be_parent_of_item_type(to_be_pasted)
        can_paste_next_to = \
            other_item.parent._can_be_parent_of_item_type(to_be_pasted) and \
            not other_item.parent.is_null()
        return can_paste_under or can_paste_next_to
        
    def _cases(self)->Set[Item]: 
        return self.__root.children.copy()

    def can_save_as_item(self,item:Item)->bool:
        return item.itype == self.__insertable

    def can_insert_under(self,parent:Item)->bool:
        parent_template = self.__creator.get_template(parent.itype)
        return self.__insertable in parent_template.child_itypes

    def copy(self, item:Item)->None:
        self.__copied_item = item.copy()

    def copy_selection(self)->None:
        if len(self.__selection)==1: self.copy(list(self.__selection)[0])

    def cut(self, item:Item)->None:
        self.__copied_item = item.copy()
        item.parent.leave(item)

    def cut_selection(self)->None:
        if len(self.__selection)==1: self.cut(list(self.__selection)[0])

    def contains_case(self,case:Item)->bool:
        return self.__root.is_parent_of(case)
    
    def duplicate(self, item:Item)->Item:
        return item.duplicate()
    
    from src.core.item import Parentage_Data
    def duplicate_as_case(self,item:Item)->Item:
        case = self.__creator.from_template(CASE_TYPE_LABEL, item.name)
        item_dupl = item.copy()
        self.__root.controller.run(
            *self.__root.command['adopt'](self.Parentage_Data(self.__root, case)),
            *case.command['adopt'](self.Parentage_Data(case, item_dupl)),
        )
        return case

    def is_groupable(self, items:Set[Item])->bool:
        if self.__insertable == "": 
            return False
        elif len(items)<2: 
            return False
        else: 
            items_list = list(items)
            orig_parent = items_list.pop(0).parent
            for item in items_list: 
                if item.parent != orig_parent: return False
        return True
    
    def is_ungroupable(self, item:Item)->bool:
        return item.itype==self.insertable and item.has_children()
    
    def group_selection(self)->Item:
        self.group(self.__selection)

    def group(self, items:Set[Item])->Item:
        if not self.is_groupable(items): 
            return ItemImpl.NULL
        else:
            orig_parent = list(items)[0].parent
            @self.__creator._controller.single_cmd()
            def move_under_group_parent()->Item:
                new_parent = self.new(orig_parent, self.insertable, name=self.__lang.label("Miscellaneous", 'new_group'))
                for item in items:
                    orig_parent.pass_to_new_parent(item, new_parent)
                return new_parent
            return move_under_group_parent()
        
    def ungroup(self, item:Item)->None:
        if not self.is_ungroupable(item): return 
        @self.__creator._controller.single_cmd()
        def do_ungrouping()->None:
            for child in item.children: 
                item.pass_to_new_parent(child, item.parent)
            item.parent.leave(item)
        do_ungrouping()

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
    
    def is_mergeable(self, items:Set[Item])->bool:
        if len(items)<2: return False
        items:List[Item] = list(items)
        first_item = items.pop(0)
        parent, itype = first_item.parent, first_item.itype
        if itype not in self.__merging_rules:
            return False
        for item in items:
            if item.parent!=parent or item.itype!=itype: return False
        return True

    def item_types_to_create(self,parent:Item)->Tuple[str,...]:
        return self.__creator.get_template(parent.itype).child_itypes

    def load_case(self, dirpath:str,name:str, ftype:FileType)->Item:
        @self.__creator._controller.single_cmd()
        def load_case_and_add_to_editor()->Item:
            case = self.__creator.load(dirpath, name, ftype)
            self.__root.adopt(case)
            return case
        return load_case_and_add_to_editor()
    
    def merge_selection(self)->Item:
        return self.merge(self.__selection)
    
    def merge(self, items:Set[Item])->Item:
        if not self.is_mergeable(items): 
            raise Exception(f"Items are not mergeable: {items}")
        items_list = list(items)
        parent, itype = items_list[0].parent, items_list[0].itype
        @self.__creator._controller.single_cmd()
        def new_merged_item()->Item:
            merge_result = self.new(parent, itype)
            merge_result.rename(self.__lang.label("Miscellaneous",'merged')+': '+merge_result.name)
            for attr_label, merge_func in self.__merging_rules[itype].items():
                merged_attr_value = merge_func([item(attr_label) for item in items])
                merge_result.attribute(attr_label).set(merged_attr_value)
            # parent must leave the original (merged) items 
            for item in items: parent.leave(item)
            return merge_result
        return new_merged_item()

    def new(self,parent:Item,itype:str,name:str="")->Item:
        if itype not in self.__creator.templates:
            raise Editor.UndefinedTemplate(itype)
        
        available_itypes = self.item_types_to_create(parent)
        if (available_itypes is None) or (itype not in available_itypes):
            raise Editor.InvalidChildTypeUnderGivenParent(
                f"Parent type: {parent.itype}, child type: {itype}."
            )
        
        @self.__creator._controller.single_cmd()
        def create_and_adopt(name:str)->Item:
            if name=="": name = self.__lang.label("Item_Types",itype)
            item = self.__creator.from_template(itype, name=name)
            parent.adopt(item)
            return item
        return create_and_adopt(name)
    
    def new_case(self,name:str)->Item:
        @self.__creator._controller.single_cmd()
        def create_and_adopt()->Item:
            case = self.__creator.from_template(CASE_TYPE_LABEL, name=name)
            self.__root.adopt(case)
            return case
        return create_and_adopt()
    
    def paste_under(self, parent:Item)->None:
        if self.__copied_item is None or not self.can_paste_under_or_next_to(self.__copied_item, parent): 
            return
        else:
            if not parent._can_be_parent_of_item_type(self.__copied_item):
                parent = parent.parent
            parent.adopt(self.__copied_item)
            self.__copied_item = None

    def paste_under_selection(self)->None:
        if len(self.__selection)==1: 
            parent = list(self.__selection)[0]
            print(parent)
            self.paste_under(parent)

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

    def select(self, item:Item) -> None:
        if item is self.__root: 
            self.__selection.clear()
        else: 
            self.__selection = {item}
            self.__selection_parent = item.parent
            self.__selection_itype = item.itype
        self.__run_actions_on_selection()

    def select_add(self, item:Item) -> None:
        if self.__selection:
            if not item.parent==self.__selection_parent: return
            elif not item.itype==self.__selection_itype: return 
        self.__selection.add(item)

    def selection_set(self, items:Set[Item])->None:
        self.__selection = items.difference({self.__root})

    def select_none(self) -> None:
        self.__selection.clear()
        self.__run_actions_on_selection()

    def set_dir_path(self,dirpath:str)->None:
        self.__creator.set_dir_path(dirpath)
    
    def undo(self)->None:
        self.__creator.undo()

    def redo(self)->None:
        self.__creator.redo()

    def __run_actions_on_selection(self)->None:
        for group in self.__actions_on_selection.values():
            for action in group: action()

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
        self.__items:Dict[str,Item_Menu_Cmds|Callable[[],None]|None] = dict()
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

    def insert_sep(self)->None:
        self.__items[f"__sep__{len(self.__items)}"] = None

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
        self.__caseview.on_selection_change(
            self.__pass_caseview_selection_to_editor
        )

    @property
    def caseview(self)->Case_View: return self.__caseview
    @property
    def editor(self)->Editor: return self.__editor

    def __pass_caseview_selection_to_editor(self)->None:
        self.editor.selection_set(self.caseview.selected_items)

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
        actions = Item_Menu_Cmds()
        actions.insert({'import_from_xml':self.import_case_from_xml})
        actions.insert({'new_case':self.__new_case})
        if self.__editor.can_paste_under_or_next_to(self.__editor.item_to_paste, self.__editor.root):
            actions.insert({'paste':lambda: self.__editor.paste_under(self.__editor.root)})
        return actions
    
    def __case_actions(self, case:Item)->Item_Menu_Cmds:
        actions = Item_Menu_Cmds()
        for itype in self.__editor.item_types_to_create(case):
            actions.insert({itype: partial(self.__editor.new, case,itype)}, "add")
        actions.insert({'edit':lambda: self.open_item_window(case)})
        actions.insert_sep()
        actions.insert({
            'copy':lambda: self.__editor.copy(case),
            'duplicate':lambda: self.__editor.duplicate(case),
            'cut': lambda: self.__editor.cut(case),
        })
        if self.__editor.can_paste_under_or_next_to(self.__editor.item_to_paste, case):
            actions.insert({'paste':lambda: self.__editor.paste_under(case)})
        actions.insert_sep()
        actions.insert({'export_to_xml': lambda: self.export_case_to_xml(case)})
        actions.insert_sep()
        actions.insert({'delete':lambda: self.__editor.remove_case(case)})
        return actions

    def __item_actions(self, item:Item)->Item_Menu_Cmds:
        actions = Item_Menu_Cmds()
        for itype in self.__editor.item_types_to_create(item):
            actions.insert({itype: partial(self.__create_new_and_open_edit_window, item ,itype)}, "add")
        actions.insert({'edit':lambda: self.open_item_window(item)})
        actions.insert_sep()
        actions.insert({
            'copy':lambda: self.__editor.copy(item),
            'duplicate':lambda: self.__editor.duplicate(item),
            'cut': lambda: self.__editor.cut(item)
        })
        if self.__editor.can_paste_under_or_next_to(self.__editor.item_to_paste, item):
            actions.insert({'paste':lambda: self.__editor.paste_under(item)})
        actions.insert_sep()
        if item in self.__editor.selection and self.__editor.selection_is_mergeable:
            actions.insert({'merge':self.__editor.merge_selection})
            actions.insert_sep()
        if item in self.__editor.selection and self.__editor.selection_is_groupable:
            actions.insert({'group':self.__editor.group_selection})
        if self.__editor.is_ungroupable(item):
            actions.insert({'ungroup': lambda: self.__editor.ungroup(item)})
        actions.insert({'delete':lambda: self.__editor.remove(item, item.parent)})
        return actions

    def __create_new_and_open_edit_window(self, parent:Item, itype:str, *args)->None:
        new_item = self.__editor.new(parent,itype)
        self.open_item_window(new_item, *args)
            
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

    @abc.abstractproperty
    def selected_items(self)->Set(Item): pass
    
    @abc.abstractmethod
    def configure(self, **kwargs)->None:
        pass

    @abc.abstractmethod
    def on_selection_change(self, func:Callable[[], None])->None:
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

