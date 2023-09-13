from __future__ import annotations
from typing import Dict, Any, Set, Callable
import dataclasses
from src.cmd.commands import Command, Controller, Composed_Command, Timing
from src.utils.naming import adjust_taken_name, strip_and_join_spaces
from src.core.attributes import attribute_factory, Attribute
import abc



class ItemManager:
    def __init__(self)->None:
        self._controller = Controller()
        self._attrfac = attribute_factory(self._controller)

    def new(self,name:str,attr_info:Dict[str,str]={})->Item:
        attributes = {}
        for label, attr_type in attr_info.items():
            attributes[label] = self._attrfac.new(attr_type,name=label) 
        return ItemImpl(name,attributes,self._controller)
    
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
        super().add(owner_id,creator_func=func,timing=timing)


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
        super().add(owner_id,creator_func=func,timing=timing)


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

        super().add(owner_id,creator_func=func,timing=timing)


from typing import Literal
Command_Type = Literal['adopt','pass_to_new_parent','rename','set_attr']
class Item(abc.ABC): # pragma: no cover
    
    def __init__(self,name:str,attributes:Dict[str,Attribute],controller:Controller)->None:
        pass

    @abc.abstractproperty
    def attributes(self)->Dict[str,Attribute]: pass
    @abc.abstractproperty
    def name(self)->str: pass
    @abc.abstractproperty
    def parent(self)->Item: pass
    @abc.abstractproperty
    def root(self)->Item: pass

    @abc.abstractmethod
    def adopt(self,child:Item)->None: pass
    
    @abc.abstractmethod
    def attribute(self,label:str)->Attribute: pass

    @abc.abstractmethod
    def on_adoption(self,owner:str,func:Callable[[Adoption_Data],Command],timing:Timing)->None: pass
    @abc.abstractmethod
    def on_passing_to_new_parent(self,owner:str,func:Callable[[Pass_To_New_Parrent_Data],Command],timing:Timing)->None: pass
    @abc.abstractmethod
    def on_renaming(self,owner:str,func:Callable[[Renaming_Data],Command],timing:Timing)->None: pass

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
        
    class AdoptionOfAncestor(Exception): pass
    class AdoptingNULL(Exception): pass
    class BlankName(Exception): pass
    class ItemAdoptsItself(Exception): pass
    class NonexistentAttribute(Exception): pass
    class NonexistentCommandType(Exception): pass


class ItemImpl(Item):

    class __ItemNull(Item):

        def __init__(self,*args,**kwargs)->None:
            pass

        @property
        def attributes(self)->Dict[str,Attribute]: return {}
        @property
        def name(self)->str: return ""
        @property
        def parent(self)->Item: return self
        @property
        def root(self)->Item: return self

        def adopt(self,child:Item)->None: 
            child.parent.pass_to_new_parent(child,self)
        def attribute(self,label:str)->Attribute: raise Item.NonexistentAttribute
        def on_adoption(self,*args)->None: pass # pragma: no cover
        def on_passing_to_new_parent(self,*args)->None: pass # pragma: no cover
        def on_renaming(self,*args)->None: pass # pragma: no cover
        def get_copy(self) -> Item: return self
        def has_children(self)->bool: return True
        def is_parent_of(self, child:Item)->bool: return child.parent is self
        def is_ancestor_of(self, child:Item)->bool: return child==self
        def pass_to_new_parent(self, child:Item, new_parent:Item)->None: 
            new_parent.adopt(child)
        def rename(self,name:str)->None: return
        def set(self, attr_name:str,value:Any)->None: raise Item.NonexistentAttribute   # pragma: no cover
        def __call__(self, attr_name:str)->Any: raise Item.NonexistentAttribute   # pragma: no cover
        def _adopt(self, child:Item)->None: return
        def _accept_parent(self,item:Item)->None: raise Item.AdoptingNULL
        def _can_be_parent_of(self,item:Item)->bool: return True   # pragma: no cover
        def _leave_child(self,child:Item)->None: return
        def _leave_parent(self,parent:Item)->None: return
        def _rename(self,name:str)->None: return


    NULL = __ItemNull()
    
    def __init__(self,name:str,attributes:Dict[str,Attribute], controller:Controller)->None:
        self.command:Dict[Command_Type,Composed_Command] = {
            'adopt':Adopt_Composed(),
            'pass_to_new_parent':PassToNewParent_Composed(),
            'rename':Rename_Composed()
        }
        self._controller = controller
        self.__attributes = attributes
        self._rename(name)
        self.__children:Set[Item] = set()
        self.__parent:Item = self.NULL

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
    
    def attribute(self,label:str)->Attribute:
        if not label in self.__attributes: raise Item.NonexistentAttribute
        else:
            return self.__attributes[label]

    def adopt(self,item:Item)->None:
        if self._can_be_parent_of(item):
            self._controller.run(*self.command['adopt'](Adoption_Data(self,item)))

    def pass_to_new_parent(self, child:Item, new_parent:Item)->None:
        if new_parent._can_be_parent_of(child):
            self._controller.run(
                self.command['pass_to_new_parent'](Pass_To_New_Parrent_Data(self,child,new_parent))
            )

    def rename(self,name:str)->None:
        self._controller.run(self.command['rename'](Renaming_Data(self,name)))

    def set(self,attrib_label:str, value:Any)->None:
        self.attribute(attrib_label).set(value)

    def on_adoption(self,owner:str,func:Callable[[Adoption_Data],Command],timing:Timing)->None:
        self.command['adopt'].add(owner, func, timing)

    def on_passing_to_new_parent(self,owner:str,func:Callable[[Pass_To_New_Parrent_Data],Command],timing:Timing)->None:
        self.command['pass_to_new_parent'].add(owner, func, timing)

    def on_renaming(self,owner:str,func:Callable[[Renaming_Data],Command],timing:Timing)->None:
        self.command['rename'].add(owner, func, timing)

    def get_copy(self)->Item:
        item_copy = ItemImpl(self.name, self.attributes, self._controller)
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

        