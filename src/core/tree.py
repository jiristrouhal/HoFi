from __future__ import annotations
from typing import List, Tuple, Dict, Any, Callable, Literal, OrderedDict
import src.core.naming
from collections import OrderedDict


import src.core.tree_templates as tt
from src.core.attributes import _Attribute, Dependent_Attr, CURRY_FORMATS


class TreeItem:

    def __init__(self, name:str, tag:str, name_attr:str="name")->None:

        self.name_attr = name_attr

        self._attributes = tt.template(tag).attributes
        self._attributes[name_attr].set(src.core.naming.strip_and_join_spaces(name))

        self.__child_tags:Tuple[str,...] = tt.template(tag).children

        self._children:List[TreeItem] = list()
        self._parent:TreeItem|None = None

        self._actions:Dict[str,Dict[str,List[Callable]]] = {}

        self._do_on_error:Dict[str,List[Callable]] = {'cannot_remove_branch_with_children':[],}

        self._data:Dict[str,Any] = dict()
        self.__tag = tag

        self.__children_allowed = bool(self.__child_tags)

        self._dependent_attributes:OrderedDict[str,Dependent_Attr] = tt.template(tag).dependent_attributes
        for attr in self._dependent_attributes.values():
            attr.set_owner(self)
        
        self._user_defined_commands:OrderedDict[str,Callable[[],None]] = \
            tt.template(tag).user_def_cmds(self)
        
        self._tree = self.its_tree

    @property
    def its_tree(self)->TreeItem:
        item = self
        while not item.parent is None:
            item = item.parent
        return item

    @property
    def name(self)->str: return self._attributes[self.name_attr].value
    @property
    def attributes(self)->Dict[str,_Attribute]: 
        return self._attributes.copy()
    @property
    def dependent_attributes(self)->OrderedDict[str,Dependent_Attr]:
        return self._dependent_attributes.copy()
    @property 
    def parent(self)->TreeItem|None: return self._parent
    @property
    def data(self)->Dict[str,Any]: return self._data
    @property
    def tag(self)->str: return self.__tag
    @property
    def child_tags(self)->Tuple[str,...]: return self.__child_tags
    @property
    def user_defined_commands(self)->OrderedDict[str,Callable[[],None]]: 
        return self._user_defined_commands

    __tree_events =  Literal['add_child','on_removal','on_renaming','on_moving','on_self_rename']

    def add_action(
        self,
        owner_id:str,
        on:__tree_events,
        action:Callable[[TreeItem],None]
        )->None: 

        if not owner_id in self._actions: self.__initialize_actions(owner_id)
        self._actions[owner_id][on].append(action)

    def __initialize_actions(self,owner_id:str)->None:
        self._actions[owner_id] = {
            'add_child': [],
            'on_removal': [],
            'on_renaming': [],
            'on_moving': [],
            'on_self_rename': [],
        }

    def add_data(self,new_key:str,value:Any)->None:
        self._data[new_key] = value

    def do_if_error_occurs(
        self,
        on:Literal['cannot_remove_branch_with_children'],
        action:Callable
        )->None:

        self._do_on_error[on].append(action)

    def set_attribute(self,attr_name:str,value:str)->None:
        if attr_name in self._attributes: self._attributes[attr_name].set(value)

    def _set_parent(self,new_parent:TreeItem)->None:
        if self._parent is not None and self in self._parent._children: 
            self._parent._children.remove(self)
        self._parent = new_parent
        self._parent._children.append(self)
        # if the name already exists under the new parent, change the current name
        self.__rename(self.name)

    def __rename(self,name:str)->None:
        name = src.core.naming.strip_and_join_spaces(name)
        if self._parent is not None:
            item_with_same_name = self._parent._find_child(name)
            while item_with_same_name is not None and not item_with_same_name==self:
                name = src.core.naming.change_name_if_already_taken(name)
                item_with_same_name = self._parent._find_child(name)
        self._attributes[self.name_attr].set(name)

    def children(self,*branches_along_the_path:str)->List[str]:
        return self._list_children(*branches_along_the_path)
    
    def _list_children(self,*branches_along_the_path:str)->List[str]:
        if branches_along_the_path:
            # list branches growing out of some child element of the current object
            lowest_level_branch = self._find_child(*branches_along_the_path)
            if lowest_level_branch is not None: return lowest_level_branch.children()
            else: return []
        return [b.name for b in self._children]

    def new(
        self,
        name:str,
        *branches_along_the_path:str,
        tag:str
        )->None:

        if not self.__children_allowed: return

        if branches_along_the_path:
            # add the new branch to some sub-branch
            parent = self._find_child(*branches_along_the_path)
            if parent is None: return
            if tag not in parent.child_tags: 
                raise KeyError(
                    f"The tag '{tag}' does not correspond to any of available child elements'\
                        templates.\n"
                    f"The available templates are {parent.child_tags}.")
            parent.new(name,tag=tag)

        else:  # add the branch directly to the current object
            child = TreeItem(name,tag,name_attr=self.name_attr)
            child._set_parent(self)
            for owner_id in self._actions:
                if not self._actions[owner_id]: 
                    self.__initialize_actions(owner_id)

            for key, foo in tt.template(tag).variable_defaults.items():
                if key in child.attributes:
                    child._attributes[key].set(foo(child))

            self.run_actions('add_child',child)

    def move_child(self,branch_path:Tuple[str,...],new_branch_parent_path:Tuple[str,...]=())->None:
        if self._does_path_point_to_child_of_branch_or_to_branch_itself(branch_path,new_branch_parent_path):
            return
        branch = self._find_child(*branch_path)
        if branch is not None:
            if len(new_branch_parent_path)==0: branch._set_parent(self)
            else:
                parent = self._find_child(*new_branch_parent_path)
                if parent is not None: branch._set_parent(parent)

            if branch._parent is not None: 
                branch.run_actions('on_moving',branch._parent)

    def remove_child(self,*branch_path:str)->None:
        if len(branch_path)>1:
            parent_branch = self._find_child(*branch_path[:-1])
            if parent_branch is not None: 
                parent_branch.remove_child(*branch_path[1:])

        branch_to_be_removed = self._find_child(branch_path[-1])
        if branch_to_be_removed is None: return

        if branch_to_be_removed.children(): 
            for action in branch_to_be_removed._do_on_error['cannot_remove_branch_with_children']: 
                action(branch_to_be_removed)
            return

        branch_to_be_removed.run_actions('on_removal',branch_to_be_removed)
        self._children.remove(branch_to_be_removed)
    
    def rename_child(self,branch_path:Tuple[str,...],new_name:str)->None:
        branch = self._find_child(*branch_path)
        if branch is None: return
        branch.rename(new_name)
        branch.run_actions('on_renaming',branch)
    
    def _does_path_point_to_child_of_branch_or_to_branch_itself(
        self,
        branch_path:Tuple[str,...],
        path:Tuple[str,...]
        )->bool:

        if len(branch_path)>len(path): return False
        for x,y in zip(branch_path, path): 
            if x!=y: return False
        return True
    
    def _find_child(self,*branch_names:str)->TreeItem|None:
        if not branch_names: return None
        parent_name = branch_names[0]
        for branch in self._children:
            if parent_name==branch.name:
                if len(branch_names)>1: 
                    return branch._find_child(*branch_names[1:])
                return branch
        return None
    
    def rename(self,name:str)->None:
        self.__rename(name)
        self.run_actions('on_self_rename',self)
 
    def run_actions(self,on:__tree_events,item:TreeItem)->None:
        for owner in self._actions:
            for action in self._actions[owner][on]: action(item)
    
    
class Tree(TreeItem): pass
class Branch(TreeItem): pass




