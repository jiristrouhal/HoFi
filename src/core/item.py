from __future__ import annotations
from collections import OrderedDict
from typing import Dict, Protocol, Any, Set, Literal, Type, Tuple, Callable, OrderedDict, List
from typing import Protocol
import dataclasses
from src.cmd.commands import Command, Controller
from src.utils.naming import adjust_taken_name, strip_and_join_spaces
import abc


        

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
class Command_Data(Protocol):
    ...


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


Command_Label = Literal['adopt','rename','pass_to_new_parent']

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
    def add_command(
        self, 
        on:Command_Label,
        owner_id:str, 
        command_creator:Callable[[Command_Data], Command],
        timing:Timing
    )->None: pass

    @abc.abstractmethod
    def get_copy(self)->Item: pass

    @abc.abstractmethod
    def has_children(self)->bool: pass

    @abc.abstractmethod
    def is_parent_of(self, child:Item)->bool: pass
    
    @abc.abstractmethod
    def is_ancestor_of(self, child:Item)->bool: pass

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


Creators_Dict = OrderedDict[str, Callable[[Command_Data], Command]]
Timing = Literal['before','after']


class External_Commands:

    def __init__(self,controller:Controller,*options:str)->None:
        self.__options = options
        self._controller = controller
        self.pre_cmd_creators:Dict[str,Creators_Dict] = {}
        self.post_cmd_creators:Dict[str,Creators_Dict] = {}
        for option in self.__options:
            self.pre_cmd_creators[option] = OrderedDict()
            self.post_cmd_creators[option] = OrderedDict()

    def add(
        self,
        on:str,
        owner_id:str, 
        command_creator:Callable[[Command_Data], Command],
        timing:Timing
        )->None:

        if on not in self.__options: 
            raise KeyError(f"{on} not in the available command types ({self.__options}).")
        cmd_dict = self.pre_cmd_creators if timing=="before" else self.post_cmd_creators
        cmd_dict[on][owner_id] = command_creator

    def run(
        self,
        on:Command_Label,   
        data:Command_Data
        )->None:

        cmd = _get_cmd(on,data)
        self._controller.run(
            *self.__get_cmds_before(on,data),
            cmd,
            *self.__get_cmds_after(on,data)
        )

    def __get_cmds_before(self, on:str, data:Command_Data)->Tuple[Command,...]:
        if on not in self.__options: 
            raise KeyError(f"{on} not in the available command types ({self.__options}).")
        return tuple([cmd(data) for cmd in self.pre_cmd_creators[on].values()])
    
    def __get_cmds_after(self, on:str, data:Command_Data)->Tuple[Command,...]:
        if on not in self.__options: 
             raise KeyError(f"{on} not in the available command types ({self.__options}).")
        return tuple([cmd(data) for cmd in self.post_cmd_creators[on].values()])
    


def command_data(command_type:str)->Type[Command_Data]:
    match command_type:
        case "pass_to_new_parent": 
            return Pass_To_New_Parrent_Data
        case "adopt":
            return Adoption_Data
        case "rename":
            return Renaming_Data
        case _:
            raise KeyError


def _get_cmd(on:Command_Label,data:Command_Data)->Command:
    match on:
        case 'adopt': 
            return Adopt(data)
        case 'pass_to_new_parent': 
            return PassToNewParent(data)
        case 'rename':
            return Rename(data.item, data.new_name)
        case _:
            raise Item.NonexistentCommandType
        

class ItemImpl(Item):

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
        def add_command(self,*args)->None: pass # pragma: no cover
        def get_copy(self) -> Item: return self
        def has_children(self)->bool: return True
        def is_parent_of(self, child:Item)->bool: return child.parent is self
        def is_ancestor_of(self, child:Item)->bool: return child==self
        def pass_to_new_parent(self, child:Item, new_parent:Item)->None: 
            new_parent.adopt(child)
        def rename(self,name:str)->None: return
        def _adopt(self, child:Item)->None: return
        def _adopt_by(self,item:Item)->None: raise Item.AdoptingNULL
        def _leave_child(self,child:Item)->None: return
        def _leave_parent(self,parent:Item)->None: return
        def _rename(self,name:str)->None: return


    NULL = __ItemNull()
    
    def __init__(self,name:str,attributes:Dict[str,Attribute], controller:Controller)->None:
        self.commands = External_Commands(controller,'adopt','rename','pass_to_new_parent')
        self.__attributes = attributes
        self._rename(name)
        self.__children:Set[Item] = set()
        self.__parent:Item = self.NULL

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

    def add_command(
        self, 
        on:Command_Label,
        owner_id:str, 
        command_creator:Callable[[Command_Data], Command],
        timing:Timing
        )->None: 

        self.commands.add(on,owner_id,command_creator,timing)


    def adopt(self,child:Item)->None:
        if child is self.NULL: 
            raise Item.AdoptingNULL
        if child.is_ancestor_of(self): 
            raise Item.HierarchyCollision
        data = Adoption_Data(self,child)
        self.commands.run('adopt', data)

    def pass_to_new_parent(self, child:Item, new_parent:Item)->None:
        if child.is_ancestor_of(new_parent): 
            raise Item.HierarchyCollision
        data = Pass_To_New_Parrent_Data(self,child,new_parent)
        self.commands.run('pass_to_new_parent', data)

    def rename(self,name:str)->None:
        self.commands.run('rename',Renaming_Data(self,name))

    def get_copy(self)->Item:
        item_copy = ItemImpl(self.name, self.attributes, self.commands._controller)
        self.parent.adopt(item_copy)
        return item_copy

    def has_children(self)->bool:
        return bool(self.__children)

    def is_parent_of(self, child:Item)->bool: 
        return child in self.__children
    
    def is_ancestor_of(self, item:Item)->bool:
        while True:
            item = item.parent
            if item==self: return True
            elif item==self.NULL: return False

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

        
