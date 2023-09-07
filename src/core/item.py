from __future__ import annotations
from collections import OrderedDict
from typing import Dict, Protocol, Any, Set, Literal, Type, Tuple, Callable, OrderedDict
import typing
import dataclasses
from src.cmd.commands import Command, Controller
from src.utils.naming import adjust_taken_name, strip_and_join_spaces
import abc


Item_Command_Type = Literal['pass_to_new_parent']
Timing = Literal['before','after']


class Attribute(Protocol): # pragma: no cover
    @property
    def value(self)->Any: ...


class ItemManager:
    def __init__(self)->None:
        self._controller = Controller()

    def new(self,name:str,attributes:Dict[str,Attribute]={})->Item:
        return ItemImpl(name,attributes,self._controller)
    
    def undo(self):
        self._controller.undo()
    
    def redo(self):
        self._controller.redo()

@dataclasses.dataclass
class Command_Data(abc.ABC):
    ...

@dataclasses.dataclass
class Renaming_Data(Command_Data):
    item:Item


@dataclasses.dataclass
class Adoption_Data(Command_Data):
    parent:Item
    child:Item



@dataclasses.dataclass
class Rename(Command):
    item:Item
    new_name:str
    original_name:str = dataclasses.field(init=False)

    def run(self):
        self.original_name = self.item.name
        self.item._rename(self.new_name)

    def undo(self):
        self.item._rename(self.original_name)
    
    def redo(self) -> None:
        self.item._rename(self.new_name)



@dataclasses.dataclass
class PassToNewParent(Command):
    parent:Item
    child:Item
    new_parent:Item
    old_name:str = dataclasses.field(init=False)

    def run(self):
        self.old_name = self.child.name
        self.child._leave_parent(self.parent)
        self.new_parent._adopt(self.child)
    
    def undo(self):
        self.child._leave_parent(self.new_parent)
        self.parent._adopt(self.child)
        self.child._rename(self.old_name)

    def redo(self):
        self.child._leave_parent(self.parent)
        self.new_parent._adopt(self.child)


class Item(abc.ABC): # pragma: no cover
    
    def __init__(self,name:str,attributes:Dict[str,Attribute],controller:Controller)->None:
        pass

    @abc.abstractproperty
    def attributes(self)->Dict[str,Attribute]: pass
    @abc.abstractproperty
    def attribute_values(self)->Dict[str,Any]: pass
    @abc.abstractproperty
    def name(self)->str: pass
    @abc.abstractproperty
    def parent(self)->Item: pass
    @abc.abstractproperty
    def root(self)->Item: pass

    @abc.abstractmethod
    def adopt(self,child:Item)->None: pass

    @abc.abstractmethod
    def do_on_adoption(
        self, 
        owner_id:str, 
        command_creator:Callable[[Adoption_Data], Command],
        timing:Timing
    )->None: pass

    @abc.abstractmethod
    def do_on_renaming(
        self, 
        owner_id:str, 
        command_creator:Callable[[Renaming_Data], Command],
        timing:Timing
    )->None: pass

    @abc.abstractmethod
    def get_copy(self)->Item: pass

    @abc.abstractmethod
    def has_children(self)->bool: pass

    @abc.abstractmethod
    def is_parent_of(self, child:Item)->bool: pass
    
    @abc.abstractmethod
    def is_predecessor_of(self, child:Item)->bool: pass

    @abc.abstractmethod
    def pass_to_new_parent(self, child:Item, new_parent:Item)->None: pass

    @abc.abstractmethod
    def rename(self,name:str)->None: pass

    @abc.abstractmethod
    def _adopt(self, child:Item)->None: pass

    @abc.abstractmethod
    def _adopt_by(self,item:Item)->None: pass

    @abc.abstractmethod
    def _leave_child(self,child:Item)->None: pass

    @abc.abstractmethod
    def _leave_parent(self,parent:Item)->None: pass

    @abc.abstractmethod
    def _rename(self,name:str)->None: pass
        
    class AdoptingNULL(Exception): pass
    class BlankName(Exception): pass
    class HierarchyCollision(Exception): pass
    class NonexistentCommandType(Exception): pass


class ItemImpl(Item):

    @dataclasses.dataclass
    class __External_Commands:
        pre_commands_creators:OrderedDict[str, Callable[[Command_Data], Command]] = \
            dataclasses.field(default_factory=OrderedDict, init=False)
        post_commands_creators:OrderedDict[str, Callable[[Command_Data], Command]] = \
            dataclasses.field(default_factory=OrderedDict, init=False)

        def add_before(
            self,
            owner_id:str, 
            command_creator:Callable[[Command_Data], Command]
            )->None:

            self.pre_commands_creators[owner_id] = command_creator

        def add_after(
            self,
            owner_id:str, 
            command_creator:Callable[[Command_Data], Command]
            )->None:

            self.post_commands_creators[owner_id] = command_creator

        def get_cmds_before(self,data:Command_Data)->Tuple[Command,...]:
            return tuple([cmd(data) for cmd in self.pre_commands_creators.values()])
        
        def get_cmds_after(self,data:Command_Data)->Tuple[Command,...]:
            return tuple([cmd(data) for cmd in self.post_commands_creators.values()])

    class __ItemNull(Item):

        def __init__(self,*args,**kwargs)->None:
            pass

        @property
        def attributes(self)->Dict[str,Attribute]: return {}
        @property
        def attribute_values(self)->Dict[str,Any]: return {}
        @property
        def name(self)->str: return ""
        @property
        def parent(self)->Item: return self
        @property
        def root(self)->Item: return self

        def adopt(self,child:Item)->None: 
            child.parent.pass_to_new_parent(child,self)
        def do_on_adoption(self,*args)->None: pass # pragma: no cover
        def do_on_renaming(self,*args)->None: pass # pragma: no cover
        def get_copy(self) -> Item: return self
        def has_children(self)->bool: return True
        def is_parent_of(self, child:Item)->bool: return child.parent is self
        def is_predecessor_of(self, child:Item)->bool: return child==self
        def pass_to_new_parent(self, child:Item, new_parent:Item)->None: 
            new_parent.adopt(child)
        def rename(self,name:str)->None: return
        def _adopt(self, child:Item)->None: return
        def _adopt_by(self,item:Item)->None: raise Item.AdoptingNULL
        def _leave_child(self,child:Item)->None: return
        def _leave_parent(self,parent:Item)->None: return
        def _rename(self,name:str)->None: return


    NULL = __ItemNull()
    
    def __init__(self,name:str,attributes:Dict[str,Attribute],controller:Controller)->None:
        self.__cmdcontroller = controller
        self.__attributes = attributes
        self._rename(name)
        self.__children:Set[Item] = set()
        self.__parent:Item = self.NULL
        self.__on_adoption = self.__External_Commands()
        self.__on_renaming = self.__External_Commands()

    @property
    def attributes(self)->Dict[str,Attribute]: 
        return self.__attributes.copy()
    
    @property
    def attribute_values(self)->Dict[str,Any]: 
        return {key:attr.value for key,attr in self.__attributes.items()}
    
    @property
    def name(self)->str: return self.__name

    @property
    def parent(self)->Item: return self.__parent

    @property
    def root(self)->Item: 
        return self if self.__parent is self.NULL else self.__parent.root
        
    def adopt(self,child:Item)->None:
        if child is self.NULL: 
            raise Item.AdoptingNULL
        if child.is_predecessor_of(self): 
            raise Item.HierarchyCollision
        
        self.__cmdcontroller.run(
            *self.__on_adoption.get_cmds_before(Adoption_Data(self,child)),
            PassToNewParent(self.NULL, child, self),
            *self.__on_adoption.get_cmds_after(Adoption_Data(self,child)),
        )

    def do_on_adoption(
        self, 
        owner_id:str, 
        command_creator:Callable[[Adoption_Data], Command],
        timing:Timing
        )->None: 

        if timing=="before": 
            self.__on_adoption.add_before(owner_id,command_creator)
        else: 
            self.__on_adoption.add_after(owner_id,command_creator)

    def do_on_renaming(
        self, 
        owner_id:str, 
        command_creator:Callable[[Renaming_Data], Command],
        timing:Timing
        )->None: 

        if timing=="before": 
            self.__on_renaming.add_before(owner_id,command_creator)
        else: 
            self.__on_renaming.add_after(owner_id,command_creator)

    def get_copy(self)->Item:
        item_copy = ItemImpl(self.name, self.attributes, self.__cmdcontroller)
        self.parent.adopt(item_copy)
        return item_copy

    def has_children(self)->bool:
        return bool(self.__children)

    def is_parent_of(self, child:Item)->bool: 
        return child in self.__children
    
    def is_predecessor_of(self, item:Item)->bool:
        while True:
            item = item.parent
            if item==self: return True
            elif item==self.NULL: return False

    def pass_to_new_parent(self, child:Item, new_parent:Item)->None:
        if child.is_predecessor_of(new_parent): raise Item.HierarchyCollision
        self.__cmdcontroller.run(
            PassToNewParent(self,child,new_parent)
        )

    def rename(self,name:str)->None:
        self.__cmdcontroller.run(
            *self.__on_renaming.get_cmds_before(Renaming_Data(self)),
            Rename(self,name),
            *self.__on_renaming.get_cmds_after(Renaming_Data(self))
        )

    def _adopt(self, child:Item)->None:
        child._adopt_by(self)
        self.__make_child_to_rename_if_its_name_already_taken(child)
        if self is child.parent:
            self.__children.add(child)

    def _adopt_by(self,item:Item)->None:
        if self.parent is self.NULL: self.__parent = item

    def _leave_child(self,child:Item)->None:
        if child in self.__children:
            self.__children.remove(child)
            child._leave_parent(self)

    def _leave_parent(self,parent:Item)->None:
        if parent is self.parent:
            if self.__parent is self.NULL: return
            self.__parent._leave_child(self)
            self.__parent = self.NULL

    def __make_child_to_rename_if_its_name_already_taken(self, child:Item):
        names = [c.name for c in self.__children]
        cname = child.name
        while cname in names: 
            names.remove(cname)
            cname = adjust_taken_name(cname)
            child._rename(cname)

    def _rename(self,name:str)->None:
        name = strip_and_join_spaces(name)
        self.__raise_if_name_is_blank(name)
        self.__name = name
    
    def __raise_if_name_is_blank(self,name:str)->None:
        if name=="": raise self.BlankName

        
