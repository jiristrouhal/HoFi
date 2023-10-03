from __future__ import annotations
from typing import Dict, Any, Set, Callable, Optional
import dataclasses
from src.cmd.commands import Command, Controller, Composed_Command, Timing, Empty_Command
from src.utils.naming import adjust_taken_name, strip_and_join_spaces
from src.core.attributes import attribute_factory, Attribute, Attribute_List, Set_Attr_Data
from src.core.attributes import Edit_AttrList_Data
import abc


@dataclasses.dataclass(frozen=True)
class Template:
    item_type:str
    attribute_info:Dict[str,str]
    child_itypes:Optional[Tuple[str,...]]


class ItemCreator:
    def __init__(self)->None:
        self._controller = Controller()
        self._attrfac = attribute_factory(self._controller)
        self.__templates:Dict[str,Template] = {}

    def add_template(
        self,
        label:str,
        attribute_info:Dict[str,str]={}, 
        child_itypes:Optional[Tuple[str,...]]=None
        )->None:

        if label in self.__templates: raise ItemCreator.TemplateAlreadyExists(label)
        if child_itypes is not None: self.__check_child_template_presence(label,child_itypes)
        self.__templates[label] = Template(label, attribute_info, child_itypes)

    def __check_child_template_presence(self, label:str, child_itypes:Tuple[str,...])->None:
        for itype in child_itypes:  
            if not ((itype in self.__templates) or (itype==label)):  
                raise ItemCreator.UndefinedTemplate(itype)

    def from_template(self,label:str)->Item:
        template = self.__templates[label]
        attributes = self.__get_attrs(template.attribute_info)
        return ItemImpl(
            template.item_type, 
            attributes, 
            self, 
            itype = template.item_type, 
            child_itypes = template.child_itypes
        )

    def new(self,name:str,attr_info:Dict[str,str]={})->Item:
        return ItemImpl(name, self.__get_attrs(attr_info), self)
    
    def undo(self):
        self._controller.undo()
    
    def redo(self):
        self._controller.redo()

    def __get_attrs(self,attribute_info:Dict[str,str])->Dict[str,Attribute]:
        attributes = {}
        for label, attr_type in attribute_info.items():
            attributes[label] = self._attrfac.new(attr_type,name=label) 
        return attributes
    
    class TemplateAlreadyExists(Exception): pass
    class UndefinedTemplate(Exception): pass


@dataclasses.dataclass
class Renaming_Data:
    item:Item
    new_name:str


@dataclasses.dataclass
class Parentage_Data:
    parent:Item
    child:Item


@dataclasses.dataclass
class Rename(Command):
    data:Renaming_Data
    original_name:str = dataclasses.field(init=False)

    def run(self):
        self.original_name = self.data.item.name
        self.data.item._rename(self.data.new_name)

    def undo(self):
        self.data.item._rename(self.original_name)
    
    def redo(self) -> None:
        self.data.item._rename(self.data.new_name)


class Rename_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return Rename

    def __call__(self, data:Renaming_Data):
        return super().__call__(data)

    def add(self, owner_id:str, func:Callable[[Renaming_Data],Command],timing:Timing)->None:
        super().add(owner_id,creator=func,timing=timing)

    def add_composed(
        self, 
        owner_id: str, 
        data_converter: Callable[[Renaming_Data], Any], 
        cmd: Composed_Command, 
        timing: Timing
        ) -> None: # pragma: no cover

        return super().add_composed(owner_id, data_converter, cmd, timing)


@dataclasses.dataclass
class Adopt(Command):
    data:Parentage_Data
    old_name:str = dataclasses.field(init=False)
    def run(self):
        self.old_name = self.data.child.name
        self.data.parent._adopt(self.data.child)
    
    def undo(self):
        self.data.child._leave_parent(self.data.parent)
        self.data.child._rename(self.old_name)

    def redo(self):
        self.data.parent._adopt(self.data.child)
    @property
    def message(self)->str:
        return f"Adopt child | '{self.data.parent.name}' adopts '{self.data.child.name}'."


class Adopt_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return Adopt

    def __call__(self, data:Parentage_Data)->Tuple[Command,...]:
        return super().__call__(data)

    def add(self, owner_id:str, func:Callable[[Parentage_Data],Command],timing:Timing)->None:
        super().add(owner_id,creator=func,timing=timing)

    def add_composed(
        self, 
        owner_id: str, 
        data_converter: 
        Callable[[Parentage_Data], Any], 
        cmd: Composed_Command, 
        timing: Timing
        ) -> None: # pragma: no cover

        return super().add_composed(owner_id, data_converter, cmd, timing)


@dataclasses.dataclass
class Leave(Command):
    data:Parentage_Data
    def run(self):
        self.data.parent._leave_child(self.data.child)
    def undo(self):
        self.data.parent._adopt(self.data.child)
    def redo(self):
        self.data.parent._leave_child(self.data.child)
    @property
    def message(self) -> str:
        return f"Leave child | '{self.data.parent.name}' leaves '{self.data.child.name}'."

class Leave_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return Leave

    def __call__(self, data:Parentage_Data)->Tuple[Command, ...]:
        return super().__call__(data)
    
    def add(self, owner_id: str, creator: Callable[[Parentage_Data], Command], timing: Timing) -> None:
        return super().add(owner_id, creator, timing)
    
    def add_composed(
        self, 
        owner_id: str, 
        data_converter: Callable[[Parentage_Data], Any], 
        cmd: Composed_Command, 
        timing: Timing
        ) -> None: # pragma: no cover

        return super().add_composed(owner_id, data_converter, cmd, timing)


from typing import Literal
Command_Type = Literal['adopt','leave','rename']
class Item(abc.ABC): # pragma: no cover

    @dataclasses.dataclass(frozen=True)
    class BindingInfo:
        func:Callable[[Any],Any]
        input_labels:Tuple[str,...]
    
    def __init__(self,name:str,attributes:Dict[str,Attribute],manager:ItemCreator)->None:
        self._manager = manager
        self.__id = str(id(self))
        self._bindings:Dict[str, Item.BindingInfo] = dict()
        self._child_attr_lists:Dict[str,Attribute_List] = dict()

    @abc.abstractproperty
    def attributes(self)->Dict[str,Attribute]: pass
    @abc.abstractproperty
    def name(self)->str: pass
    @abc.abstractproperty
    def parent(self)->Item: pass
    @abc.abstractproperty
    def root(self)->Item: pass
    @abc.abstractproperty
    def children(self)->Set[Item]: pass
    @property
    def controller(self)->Controller: return self._manager._controller
    @property
    def id(self)->str: return self.__id
    @property
    def itype(self)->str: return ""
    @abc.abstractproperty
    def child_itypes(self)->Optional[Tuple[str,...]]: pass

    @abc.abstractmethod
    def bind(self, output_name:str, func:Callable[[Any],Any], *input_names:str)->None:
        """
        A following convention is used for specifiying the dependency inputs:
            'x' ... attribute named 'x', owned by this item\n
            '[x:integer]' ... list of all attributes named 'x' owned by this item's children. The expected type of the attributes must be put after the label; both must be separated with a colon
        Naming is whitespace- and case- sensitive (e.g. 'x' is different from ' x' and from 'X').
        """
        pass

    @abc.abstractmethod
    def adopt(self,child:Item)->None: pass
    
    @abc.abstractmethod
    def attribute(self,label:str)->Attribute: pass

    @abc.abstractmethod
    def free(self,output_name:str)->None: pass

    @abc.abstractmethod
    def has_attribute(self,label:str)->bool: pass

    @abc.abstractmethod
    def on_adoption(self,owner:str,func:Callable[[Parentage_Data],Command],timing:Timing)->None: pass
    @abc.abstractmethod
    def on_leaving(self,owner:str,func:Callable[[Parentage_Data],Command],timing:Timing)->None: pass
    @abc.abstractmethod
    def on_renaming(self,owner:str,func:Callable[[Renaming_Data],Command],timing:Timing)->None: pass

    @abc.abstractmethod
    def _create_child_attr_list(self, value_type:str, child_attr_label:str)->None: pass

    @abc.abstractmethod
    def duplicate(self)->Item: pass

    @abc.abstractmethod
    def has_children(self)->bool: pass

    @abc.abstractmethod
    def is_parent_of(self, child:Item)->bool: pass
    
    @abc.abstractmethod
    def is_ancestor_of(self, child:Item)->bool: pass

    @abc.abstractmethod
    def leave(self, child:Item)->None: pass

    @abc.abstractmethod
    def pass_to_new_parent(self, child:Item, new_parent:Item)->None: pass

    @abc.abstractmethod
    def pick_child(self, name:str)->Item: pass 

    @abc.abstractmethod
    def rename(self,name:str)->None: pass

    @abc.abstractmethod
    def set(self, attribute_name:str, value:Any)->None: pass

    @abc.abstractmethod
    def __call__(self, attr_name:str)->Any: pass

    @abc.abstractmethod
    def _adopt(self, child:Item)->None: pass

    @abc.abstractmethod
    def _accept_parent(self,item:Item)->None: pass

    @abc.abstractmethod
    def _apply_binding_info(self)->None: pass

    @abc.abstractmethod
    def _copy_bindings(self, dupl:Item)->None: pass 

    @abc.abstractmethod
    def _can_be_parent_of(self,item:Item)->bool: pass

    @abc.abstractmethod
    def _leave_child(self,child:Item)->None: pass

    @abc.abstractmethod
    def _leave_parent(self,parent:Item)->None: pass

    @abc.abstractmethod
    def _rename(self,name:str)->None: pass

    @abc.abstractmethod
    def _duplicate_items(self)->Item: pass
        
    class AdoptionOfAncestor(Exception): pass
    class AdoptingNULL(Exception): pass
    class BlankName(Exception): pass
    class CannotAdoptItemOfType(Exception): pass
    class ItemAdoptsItself(Exception): pass
    class NonexistentAttribute(Exception): pass
    class NonexistentCommandType(Exception): pass
    class NonexistentChildValueGroup(Exception): pass



from src.core.attributes import Append_To_Attribute_List, Remove_From_Attribute_List, AbstractAttribute
from typing import Tuple, List

class ItemImpl(Item):

    class __ItemNull(Item):
        def __init__(self,*args,**kwargs)->None:
            self.__children:Set[Item] = set()
            self._child_attr_lists:Dict = dict()
        @property
        def attributes(self)->Dict[str,Attribute]: return {}
        @property
        def name(self)->str: return "NULL"
        @property
        def parent(self)->Item: return self
        @property
        def root(self)->Item: return self
        @property
        def children(self)->Set[Item]: raise self.CannotAccessChildrenOfNull
        @property
        def itype(self)->str: return ""   # pragma: no cover
        @property
        def child_itypes(self)->Optional[Tuple[str,...]]: return None   # pragma: no cover

        def bind(self,*args)->None: raise self.SettingDependencyOnNull
        def free(self,*args)->None: raise self.SettingDependencyOnNull
        def adopt(self,child:Item)->None: 
            if child.parent is not self: child.parent.leave(child)
        def attribute(self,label:str)->Attribute: raise Item.NonexistentAttribute # pragma: no cover
        def has_attribute(self,label:str)->bool: return False
        def on_adoption(self,*args)->None: pass # pragma: no cover
        def on_leaving(self,*args)->None: pass # pragma: no cover
        def on_renaming(self,*args)->None: pass # pragma: no cover
        def _create_child_attr_list(self,*args)->None: raise self.AddingAttributeToNullItem
        def duplicate(self)->ItemImpl.__ItemNull: return self
        def has_children(self)->bool: return True
        def is_parent_of(self, child:Item)->bool: return child.parent is self
        def is_ancestor_of(self, child:Item)->bool: return child==self
        def leave(self, child:Item)->None: raise self.NullCannotLeaveChild
        def pass_to_new_parent(self, child:Item, new_parent:Item)->None: 
            new_parent.adopt(child)
        def pick_child(self, name:str)->Item: raise self.CannotAccessChildrenOfNull
        def rename(self,name:str)->None: return
        def set(self, attr_name:str,value:Any)->None: raise Item.NonexistentAttribute   # pragma: no cover
        def __call__(self, attr_name:str)->Any: raise Item.NonexistentAttribute   # pragma: no cover
        def _adopt(self, child:Item)->None: return # pragma: no cover
        def _accept_parent(self,item:Item)->None: raise Item.AdoptingNULL
        def _apply_binding_info(self)->None: pass # pragma: no cover
        def _copy_bindings(self, dupl:Item)->None: pass # pragma: no cover
        def _can_be_parent_of(self,item:Item)->bool: return True   # pragma: no cover
        def _leave_child(self,child:Item)->None: return
        def _leave_parent(self,parent:Item)->None: return
        def _rename(self,name:str)->None: return
        def _duplicate_items(self)->Item: return self # pragma: no cover

        class AddingAttributeToNullItem(Exception): pass
        class CannotAccessChildrenOfNull(Exception): pass
        class NullCannotLeaveChild(Exception): pass
        class SettingDependencyOnNull(Exception): pass

    NULL = __ItemNull()

    
    def __init__(self,name:str,attributes:Dict[str,Attribute], manager:ItemCreator, itype:str="", child_itypes:Optional[Tuple[str,...]]=None)->None:
        super().__init__(name,attributes,manager)
        self.__attributes = attributes
        self._rename(name)
        self.__children:Set[Item] = set()
        self.__parent:Item = self.NULL
        self._bindings:Dict[str, Item.BindingInfo] = dict()
        self.command:Dict[Command_Type,Composed_Command] = {
            'adopt':Adopt_Composed(),
            'leave':Leave_Composed(),
            'rename':Rename_Composed()
        }
        self.__itype = itype
        self.__child_itypes = child_itypes

    @property
    def attributes(self)->Dict[str,Attribute]: 
        return self.__attributes.copy()
    @property
    def name(self)->str: 
        return self.__name
    @property
    def parent(self)->Item: 
        return self.__parent
    @property
    def root(self)->Item: 
        return self if self.__parent is self.NULL else self.__parent.root
    @property
    def children(self)->Set[Item]:
        return self.__children.copy()
    @property
    def itype(self)->str: return self.__itype
    @property
    def child_itypes(self)->Optional[Tuple[str,...]]: return self.__child_itypes
 
    def attribute(self,label:str)->Attribute:
        if not label in self.__attributes: 
            raise Item.NonexistentAttribute(label)
        else:
            return self.__attributes[label]
        
    def bind(self, output_name:str, func:Callable[[Any], Any], *input_names:str)->None:
        output = self.attribute(output_name)
        inputs = self.__collect_input_attributes(input_names)
        output.add_dependency(func, *inputs)
        self._bindings[output_name] = ItemImpl.BindingInfo(func, input_names)

    def __collect_input_attributes(self, input_labels:Tuple[str,...])->List[AbstractAttribute]:
        inputs:List[AbstractAttribute] = list()
        for input_label in input_labels:
            if self.__is_child_attributes_label(input_label):
                label, value_type = input_label[1:-1].split(":")
                if label not in self._child_attr_lists:
                    self._create_child_attr_list(value_type, label)
                inputs.append(self._child_attr_lists[label])
            else:
                inputs.append(self.attribute(input_label))
        return inputs
    
    @staticmethod
    def __is_child_attributes_label(label)->bool: 
        if len(label)<3: 
            return False
        else:
            return label[0]=='[' and label[-1]==']'

    def free(self, output_name:str)->None:
        self.attribute(output_name).break_dependency()
        self._bindings.pop(output_name)
        
    def has_attribute(self, label:str)->bool:
        return label in self.__attributes
    
    def adopt(self,item:Item)->None:
        if self is item.parent: return
        if self._can_be_parent_of(item):
            self.controller.run(*self.command['adopt'](Parentage_Data(self,item)))

    def leave(self, child:Item)->None:
        self.controller.run(*self.command['leave'](Parentage_Data(self,child)))
    
    def __check_attr_type_matches_list_type(
        self,
        alist:Attribute_List,
        attribute:AbstractAttribute
        )->None:
        
        if not alist.type==attribute.type: 
            raise self.ChildAttributeTypeConflict

    def _create_child_attr_list(self, value_type:str, child_attr_label:str)->None:
        alist = self._manager._attrfac.newlist(atype=value_type, name=child_attr_label+' (children)')
        
        for child in self.__children: 
            if child_attr_label in child.attributes: 
                self.__check_attr_type_matches_list_type(alist,child.attribute(child_attr_label))
                alist.append(child.attribute(child_attr_label))
        
        def adopt_cmd(data:Parentage_Data)->Command:
            if not data.child.has_attribute(child_attr_label): return Empty_Command()
            self.__check_attr_type_matches_list_type(alist, data.child.attribute(child_attr_label))
            cmd_data = Edit_AttrList_Data(alist,data.child.attribute(child_attr_label))
            return Append_To_Attribute_List(cmd_data)
            
        def leave_child_cmd(data:Parentage_Data)->Command:
            if not data.child.has_attribute(child_attr_label): return Empty_Command()
            cmd_data = Edit_AttrList_Data(alist,data.child.attribute(child_attr_label))
            return Remove_From_Attribute_List(cmd_data)

        def converter(data:Parentage_Data)->Set_Attr_Data:
            value_getter = lambda: alist.value
            return Set_Attr_Data(alist, value_getter)

        self.command['adopt'].add(alist.id, adopt_cmd, 'post')
        self.command['adopt'].add_composed(alist.id, converter, alist.command['set'], 'post')
        self.command['leave'].add(alist.id, leave_child_cmd, 'post')
        self.command['leave'].add_composed(alist.id, converter, alist.command['set'], 'post')

        self._child_attr_lists[child_attr_label] = alist
    
    def pass_to_new_parent(self, child:Item, new_parent:Item)->None:
        if new_parent._can_be_parent_of(child) and isinstance(new_parent, ItemImpl):
            self.controller.run(
                *self.command['leave'](Parentage_Data(self,child)),
                *new_parent.command['adopt'](Parentage_Data(new_parent,child))
            )   

    def pick_child(self,name:str)->Item:
        name = strip_and_join_spaces(name)
        for child in self.__children: 
            if child.name==name: return child
        return ItemImpl.NULL

    def rename(self,name:str)->None:
        self.controller.run(*self.command['rename'](Renaming_Data(self,name)))

    def set(self,attrib_label:str, value:Any)->None:
        self.attribute(attrib_label).set(value)

    def on_adoption(self,owner:str,func:Callable[[Parentage_Data],Command],timing:Timing)->None:
        self.command['adopt'].add(owner, func, timing)

    def on_leaving(self,owner:str,func:Callable[[Parentage_Data],Command],timing:Timing)->None:
        self.command['leave'].add(owner, func, timing)

    def on_renaming(self,owner:str,func:Callable[[Renaming_Data],Command],timing:Timing)->None:
        self.command['rename'].add(owner, func, timing)

    def duplicate(self)->Item:
        the_duplicate = self._duplicate_items()
        self._copy_bindings(the_duplicate)
        self.parent.adopt(the_duplicate)
        return the_duplicate

    def has_children(self)->bool:
        return bool(self.__children)

    def is_parent_of(self, child:Item)->bool: 
        return child in self.__children
    
    def is_ancestor_of(self, item:Item)->bool:
        while True:
            item = item.parent
            if item==self: return True
            elif item==self.NULL: return False

    def __call__(self, attr_name:str)->Any: 
        if attr_name not in self.attributes: 
            raise Item.NonexistentAttribute
        else:
            return self.attribute(attr_name).value

    def _accept_parent(self,item:Item)->None:
        if self.parent is self.NULL: self.__parent = item

    def _adopt(self, child:Item)->None:
        child._accept_parent(self)
        self.__make_child_to_rename_if_its_name_already_taken(child)
        if self is child.parent:
            self.__children.add(child)

    def _can_be_parent_of(self,item:Item)->bool:
        if self.child_itypes is not None:
            if item.itype not in self.child_itypes: raise Item.CannotAdoptItemOfType(item.itype)

        if item.is_ancestor_of(self): raise Item.AdoptionOfAncestor
        elif item==self: raise Item.ItemAdoptsItself
        else: return True

    def _duplicate_items(self)->ItemImpl:
        dupl = ItemImpl(self.name, self.__attributes_copy(), self._manager)
        for attr in dupl.__attributes.values():
            if attr.dependent: attr.break_dependency()
        for child in self.__children:
            child_duplicate = child._duplicate_items()
            dupl._adopt(child_duplicate)
        return dupl
    
    def _apply_binding_info(self)->None:
        for output_name, info in self._bindings.items():
            self.bind(output_name, info.func, *info.input_labels)
    
    def _copy_bindings(self, dupl:Item)->None:
        dupl._bindings = self._bindings.copy()
        dupl._apply_binding_info()
        for child, child_dupl in zip(self.__children, dupl.children):
            child._copy_bindings(child_dupl)

    def _leave_child(self,child:Item)->None:
        if child in self.__children:
            self.__children.remove(child)
            child._leave_parent(self)

    def _leave_parent(self,parent:Item)->None:
        if parent is self.parent:
            if self.__parent is self.NULL: return
            self.__parent._leave_child(self)
            self.__parent = self.NULL

    def _rename(self,name:str)->None:
        name = strip_and_join_spaces(name)
        self.__raise_if_name_is_blank(name)
        self.__name = name

    
    def __attributes_copy(self)->Dict[str,Attribute]:
        attr_copy:Dict[str,Attribute] = {}
        for label, attr in self.attributes.items():
            attr_copy[label] = attr.copy()
        return attr_copy
    
    def __make_child_to_rename_if_its_name_already_taken(self, child:Item):
        names = [c.name for c in self.__children]
        cname = child.name
        while cname in names: 
            names.remove(cname)
            cname = adjust_taken_name(cname)
            child._rename(cname)
    
    def __raise_if_name_is_blank(self,name:str)->None:
        if name=="": raise self.BlankName


    class ChildAttributeTypeConflict(Exception): pass
        