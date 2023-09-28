from __future__ import annotations
from typing import Dict, Any, Set, Callable
import dataclasses
from src.cmd.commands import Command, Controller, Composed_Command, Timing, Empty_Command
from src.utils.naming import adjust_taken_name, strip_and_join_spaces
from src.core.attributes import attribute_factory, Attribute, Attribute_List, Set_Attr_Data, Set_Attr_Composed
from src.core.attributes import Edit_AttrList_Data
import abc


class ItemManager:
    def __init__(self)->None:
        self._controller = Controller()
        self._attrfac = attribute_factory(self._controller)

    def new(self,name:str,attr_info:Dict[str,str]={})->Item:
        attributes = {}
        for label, attr_type in attr_info.items():
            attributes[label] = self._attrfac.new(attr_type,name=label) 
        return ItemImpl(name,attributes, self)
    
    def undo(self):
        self._controller.undo()
    
    def redo(self):
        self._controller.redo()


@dataclasses.dataclass
class Renaming_Data:
    item:Item
    new_name:str


@dataclasses.dataclass
class Adoption_Data:
    parent:Item
    child:Item


@dataclasses.dataclass
class Pass_To_New_Parrent_Data:
    parent:Item
    child:Item
    new_parent:Item


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

    def add_composed(self, owner_id: str, data_converter: Callable[[Renaming_Data], Any], cmd: Composed_Command, timing: Timing) -> None:
        return super().add_composed(owner_id, data_converter, cmd, timing)


@dataclasses.dataclass
class Adopt(Command):
    data:Adoption_Data
    old_name:str = dataclasses.field(init=False)
    def run(self):
        self.old_name = self.data.child.name
        self.data.parent._adopt(self.data.child)
    
    def undo(self):
        self.data.child._leave_parent(self.data.parent)
        self.data.child._rename(self.old_name)

    def redo(self):
        self.data.parent._adopt(self.data.child)


class Adopt_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return Adopt

    def __call__(self, data:Adoption_Data):
        return super().__call__(data)

    def add(self, owner_id:str, func:Callable[[Adoption_Data],Command],timing:Timing)->None:
        super().add(owner_id,creator=func,timing=timing)

    def add_composed(self, owner_id: str, data_converter: Callable[[Adoption_Data], Any], cmd: Composed_Command, timing: Timing) -> None:
        return super().add_composed(owner_id, data_converter, cmd, timing)


@dataclasses.dataclass
class PassToNewParent(Command):
    data:Pass_To_New_Parrent_Data
    old_name:str = dataclasses.field(init=False)

    def run(self):
        self.old_name = self.data.child.name
        self.data.child._leave_parent(self.data.parent)
        self.data.new_parent._adopt(self.data.child)
    
    def undo(self):
        self.data.child._leave_parent(self.data.new_parent)
        self.data.parent._adopt(self.data.child)
        self.data.child._rename(self.old_name)

    def redo(self):
        self.data.child._leave_parent(self.data.parent)
        self.data.new_parent._adopt(self.data.child)


class PassToNewParent_Composed(Composed_Command):
    @staticmethod
    def cmd_type(): return PassToNewParent

    def __call__(self, data:Pass_To_New_Parrent_Data):
        return super().__call__(data)

    def add(
        self, 
        owner_id:str, 
        func:Callable[[Pass_To_New_Parrent_Data],Command],
        timing:Timing)->None:

        super().add(owner_id,creator=func,timing=timing)

    def add_composed(self, owner_id: str, data_converter: Callable[[Pass_To_New_Parrent_Data], Any], cmd: Composed_Command, timing: Timing) -> None:
        return super().add_composed(owner_id, data_converter, cmd, timing)


from typing import Literal
Command_Type = Literal['adopt','pass_to_new_parent','rename']
class Item(abc.ABC): # pragma: no cover
    
    def __init__(self,name:str,attributes:Dict[str,Attribute],manager:ItemManager)->None:
        self._manager = manager
        self.__id = str(id(self))

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

    @abc.abstractmethod
    def bind(self, output_name:str, func:Callable[[Any],Any], *input_names:str)->None: pass

    @abc.abstractmethod
    def adopt(self,child:Item)->None: pass
    
    @abc.abstractmethod
    def attribute(self,label:str)->Attribute: pass

    @abc.abstractmethod
    def free(self,output_name:str)->None: pass

    @abc.abstractmethod
    def has_attribute(self,label:str)->bool: pass

    @abc.abstractmethod
    def on_adoption(self,owner:str,func:Callable[[Adoption_Data],Command],timing:Timing)->None: pass
    @abc.abstractmethod
    def on_passing_to_new_parent(self,owner:str,func:Callable[[Pass_To_New_Parrent_Data],Command],timing:Timing)->None: pass
    @abc.abstractmethod
    def on_renaming(self,owner:str,func:Callable[[Renaming_Data],Command],timing:Timing)->None: pass

    @abc.abstractmethod
    def collect_child_values(self, value_type:str, child_attribute_label:str)->None: pass

    @abc.abstractmethod
    def child_values(self, label:str)->Attribute_List: pass

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
    class ItemAdoptsItself(Exception): pass
    class NonexistentAttribute(Exception): pass
    class NonexistentCommandType(Exception): pass
    class NonexistentChildValueGroup(Exception): pass



from src.core.attributes import Append_To_Attribute_List, Remove_From_Attribute_List
from typing import Tuple

class ItemImpl(Item):

    class __ItemNull(Item):
        def __init__(self,*args,**kwargs)->None:
            self.__children:Set[Item] = set()

        @property
        def attributes(self)->Dict[str,Attribute]: return {}
        @property
        def name(self)->str: return ""
        @property
        def parent(self)->Item: return self
        @property
        def root(self)->Item: return self
        @property
        def children(self)->Set[Item]: return self.__children

        def bind(self,*args)->None: raise self.SettingDependencyOnNull
        def free(self,*args)->None: raise self.SettingDependencyOnNull
        def adopt(self,child:Item)->None: 
            if child.parent is self: return
            child.parent.pass_to_new_parent(child,self)
        def attribute(self,label:str)->Attribute: raise Item.NonexistentAttribute
        def has_attribute(self,label:str)->bool: return False
        def on_adoption(self,*args)->None: pass # pragma: no cover
        def on_passing_to_new_parent(self,*args)->None: pass # pragma: no cover
        def on_renaming(self,*args)->None: pass # pragma: no cover
        def child_values(self, label:str)->Attribute_List: raise Item.NonexistentAttribute
        def collect_child_values(self,*args)->Any: return None 
        def duplicate(self) -> Item: return self
        def has_children(self)->bool: return True
        def is_parent_of(self, child:Item)->bool: return child.parent is self
        def is_ancestor_of(self, child:Item)->bool: return child==self
        def leave(self, child:Item)->None: pass
        def pass_to_new_parent(self, child:Item, new_parent:Item)->None: 
            new_parent.adopt(child)
        def pick_child(self, name:str)->Item: return self
        def rename(self,name:str)->None: return
        def set(self, attr_name:str,value:Any)->None: raise Item.NonexistentAttribute   # pragma: no cover
        def __call__(self, attr_name:str)->Any: raise Item.NonexistentAttribute   # pragma: no cover
        def _adopt(self, child:Item)->None: return
        def _accept_parent(self,item:Item)->None: raise Item.AdoptingNULL
        def _can_be_parent_of(self,item:Item)->bool: return True   # pragma: no cover
        def _leave_child(self,child:Item)->None: return
        def _leave_parent(self,parent:Item)->None: return
        def _rename(self,name:str)->None: return
        def _duplicate_items(self)->Item: return self # pragma: no cover

        class SettingDependencyOnNull(Exception):pass

    NULL = __ItemNull()


    @dataclasses.dataclass(frozen=True)
    class __BindingInfo:
        func:Callable[[Any],Any]
        input_labels:Tuple[str,...]

    
    def __init__(self,name:str,attributes:Dict[str,Attribute], manager:ItemManager)->None:
        super().__init__(name,attributes,manager)
        self.command:Dict[Command_Type,Composed_Command] = {
            'adopt':Adopt_Composed(),
            'pass_to_new_parent':PassToNewParent_Composed(),
            'rename':Rename_Composed()
        }
        self.__attributes = attributes
        self._rename(name)
        self.__children:Set[Item] = set()
        self.__parent:Item = self.NULL
        self._child_values:Dict[str,Attribute_List] = dict()
        self.__bindings:Dict[str, ItemImpl.__BindingInfo] = dict()

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
 
    def attribute(self,label:str)->Attribute:
        if not label in self.__attributes: raise Item.NonexistentAttribute
        else:
            return self.__attributes[label]
        
    def bind(self, output_name:str, func:Callable[[Any], Any], *input_names:str)->None:
        output = self.attribute(output_name)
        output.add_dependency(func, *[self.attribute(name) for name in input_names])
        self.__bindings[output_name] = ItemImpl.__BindingInfo(func, input_names)
    
    def free(self, output_name:str)->None:
        self.attribute(output_name).break_dependency()
        self.__bindings.pop(output_name)
        
    def has_attribute(self, label:str)->bool:
        return label in self.__attributes
    
    def adopt(self,item:Item)->None:
        if self is item.parent: return
        if self._can_be_parent_of(item):
            self.controller.run(*self.command['adopt'](Adoption_Data(self,item)))
    
    def child_values(self, label:str)->Attribute_List:
        if label not in self._child_values: raise Item.NonexistentChildValueGroup
        return self._child_values[label]

    def collect_child_values(self, value_type:str, attribute_label:str)->None:
        alist = self._manager._attrfac.newlist(atype=value_type)
        for child in self.__children: 
            if attribute_label in child.attributes: 
                alist.append(child.attribute(attribute_label))
        
        def append_cmd(data:Adoption_Data)->Command:
            if data.child.has_attribute(attribute_label):
                cmd_data = Edit_AttrList_Data(alist,data.child.attribute(attribute_label))
                return Append_To_Attribute_List(cmd_data)
            else:
                return Empty_Command()
            
        def pass_to_new_parent_cmd(data:Pass_To_New_Parrent_Data)->Command:
            if data.child.has_attribute(attribute_label):
                cmd_data = Edit_AttrList_Data(alist,data.child.attribute(attribute_label))
                return Remove_From_Attribute_List(cmd_data)
            else:
                return Empty_Command()
            
        def set_cmd_converter(data:Adoption_Data)->Set_Attr_Data:
            value_getter = lambda: alist.value
            return Set_Attr_Data(alist, value_getter)

        self.command['adopt'].add(self.id, append_cmd, 'post')
        self.command['adopt'].add_composed(
            self.id, 
            set_cmd_converter, 
            alist.command['set'], 
            'post'
        )

        self.command['pass_to_new_parent'].add(self.id, pass_to_new_parent_cmd, 'post')
        self.command['pass_to_new_parent'].add_composed(
            self.id, 
            set_cmd_converter, 
            alist.command['set'], 
            'post'
        )

        self._child_values[attribute_label] = alist
    
    def leave(self, child:Item)->None:
        self.pass_to_new_parent(child, ItemImpl.NULL)

    def pass_to_new_parent(self, child:Item, new_parent:Item)->None:
        if new_parent._can_be_parent_of(child):
            self.controller.run(
                self.command['pass_to_new_parent'](Pass_To_New_Parrent_Data(self,child,new_parent))
            )

    def pick_child(self,name:str)->Item:
        name = strip_and_join_spaces(name)
        for child in self.__children: 
            if child.name==name: return child
        return ItemImpl.NULL

    def rename(self,name:str)->None:
        self.controller.run(self.command['rename'](Renaming_Data(self,name)))

    def set(self,attrib_label:str, value:Any)->None:
        self.attribute(attrib_label).set(value)

    def on_adoption(self,owner:str,func:Callable[[Adoption_Data],Command],timing:Timing)->None:
        self.command['adopt'].add(owner, func, timing)

    def on_passing_to_new_parent(self,owner:str,func:Callable[[Pass_To_New_Parrent_Data],Command],timing:Timing)->None:
        self.command['pass_to_new_parent'].add(owner, func, timing)

    def on_renaming(self,owner:str,func:Callable[[Renaming_Data],Command],timing:Timing)->None:
        self.command['rename'].add(owner, func, timing)

    def duplicate(self)->Item:
        the_duplicate = self._duplicate_items()
        self.__copy_bindings(the_duplicate)
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
    
    def __apply_binding_info(self)->None:
        for output_name, info in self.__bindings.items():
            self.bind(output_name, info.func, *info.input_labels)
    
    def __copy_bindings(self, dupl:ItemImpl)->None:
        dupl.__bindings = self.__bindings.copy()
        dupl.__apply_binding_info()
        for child, child_dupl in zip(self.__children, dupl.__children):
            if isinstance(child, ItemImpl) and isinstance(child_dupl, ItemImpl):
                child.__copy_bindings(child_dupl)

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


        