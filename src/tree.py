from __future__ import annotations
from typing import List, Tuple, Dict, Any, Callable, Literal, OrderedDict
import abc
import src.naming
from collections import OrderedDict


DEFAULT_TAG = "Item"


class TreeItem(abc.ABC):

    def __init__(
        self,
        name:str,
        attributes:Dict[str,Any]=OrderedDict(),
        tag:str = DEFAULT_TAG, 
        type:Literal['leaf','branch']='branch'
        )->None:

        self._attributes = OrderedDict()
        self._attributes["name"] = name.strip()
        for attr, value in attributes.items():
            self._attributes[attr] = str(value)
        self._children:List[TreeItem] = list()
        self._parent:TreeItem|None = None

        self._actions:Dict[str,Dict[str,List[Callable]]] = {}

        self._do_on_error:Dict[str,List[Callable]] = {
            'cannot_remove_branch_with_children':[],
        }
        self._data:Dict[str,Any] = dict()
        self.__type = type
        self.__tag = tag


    @property
    def name(self)->str: return self._attributes["name"]
    @property
    def attributes(self)->Dict[str,str]: return self._attributes.copy()
    @property 
    def parent(self)->TreeItem|None: return self._parent
    @property
    def data(self)->Dict[str,Any]: return self._data.copy()
    @property
    def type(self)->str: return self.__type
    @property
    def tag(self)->str: return self.__tag

    def add_action(
        self,
        owner_id:str,
        on:Literal['add_branch','on_removal','on_renaming','on_moving','on_self_rename'],
        action:Callable[[TreeItem],None]
        )->None: 

        if not owner_id in self._actions: self.__initialize_actions(owner_id)
        self._actions[owner_id][on].append(action)

    def __initialize_actions(self,owner_id:str)->None:
        self._actions[owner_id] = {
            'add_branch': [],
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
        if attr_name in self._attributes: self._attributes[attr_name] = value

    def _set_parent(self,new_parent:TreeItem)->None:
        if self._parent is not None: 
            self._parent._children.remove(self)
        # if the name already exists under the new parent, change the current name
        name = src.naming.strip_and_join_spaces(self.name)
        while new_parent._find_child(name) is not None: 
            name = src.naming.change_name_if_already_taken(name)
        self._attributes["name"] = name
        self._parent = new_parent
        self._parent._children.append(self)

    def rename(self,name:str)->None:
        name = src.naming.strip_and_join_spaces(name)
        if self._parent is not None:
            item_with_same_name = self._parent._find_child(name)
            while item_with_same_name is not None and not item_with_same_name==self:
                name = src.naming.change_name_if_already_taken(name)
                item_with_same_name = self._parent._find_child(name)
        self._attributes["name"] = name

        for owner in self._actions:
            for action in self._actions[owner]['on_self_rename']: action(self)

    def branches(self,*branches_along_the_path:str)->List[str]:
        return self._list_children(*branches_along_the_path,type='branch')
    
    def leaves(self,*branches_along_the_path:str)->List[str]:
        return self._list_children(*branches_along_the_path,type='leaf')
    
    def _list_children(self,*branches_along_the_path:str,type:Literal['leaf','branch','all'])->List[str]:
        if branches_along_the_path:
            # list branches growing out of some child element of the current object
            lowest_level_branch = self._find_child(*branches_along_the_path)
            if lowest_level_branch is not None:
                return lowest_level_branch.branches()
            else:
                return []
        # display branches growint out of the current object (branch, tree, ...)
        if type=='all':
            return [b.name for b in self._children]
        return [b.name for b in self._children if b.type==type]

    def new(
        self,
        name:str,
        *branches_along_the_path:str,
        tag:str = DEFAULT_TAG,
        attributes:Dict[str,Any]=dict(),
        type:Literal['branch','leaf'] = 'branch',
        )->None:

        if self.__type=='leaf': return 

        if branches_along_the_path:
            # add the new branch to some sub-branch
            smallest_parent_branch = self._find_child(*branches_along_the_path)
            if smallest_parent_branch is None: return
            smallest_parent_branch.new(name,attributes={})
        else:  # add the branch directly to the current object
            branch = Branch(name,attributes,type=type,tag=tag)
            branch._set_parent(self)
            for owner_id in self._actions:
                if not self._actions[owner_id]: 
                    self.__initialize_actions(owner_id)
                for action in self._actions[owner_id]['add_branch']: 
                    action(branch)
        
    def move_child(self,branch_path:Tuple[str,...],new_branch_parent_path:Tuple[str,...]=())->None:
        if self._does_path_point_to_child_of_branch_or_to_branch_itself(branch_path,new_branch_parent_path):
            return
        branch = self._find_child(*branch_path)
        if branch is not None:
            if len(new_branch_parent_path)==0: branch._set_parent(self)
            else:
                parent = self._find_child(*new_branch_parent_path)
                if parent is not None: branch._set_parent(parent)

            for owner in branch._actions:
                for action in branch._actions[owner]['on_moving']: 
                    action(parent)

    def remove_child(self,*branch_path:str)->None:
        if len(branch_path)>1:
            parent_branch = self._find_child(*branch_path[:-1])
            if parent_branch is not None: 
                parent_branch.remove_child(*branch_path[1:])

        branch_to_be_removed = self._find_child(branch_path[-1])
        if branch_to_be_removed is None: return

        if branch_to_be_removed.branches(): 
            for action in branch_to_be_removed._do_on_error['cannot_remove_branch_with_children']: 
                action(branch_to_be_removed)
            return

        for owner in branch_to_be_removed._actions:
            for action in branch_to_be_removed._actions[owner]['on_removal']: 
                action(branch_to_be_removed)

        self._children.remove(branch_to_be_removed)
    
    def rename_child(self,branch_path:Tuple[str,...],new_name:str)->None:
        branch = self._find_child(*branch_path)
        if branch is None: return
        branch.rename(new_name)

        for owner in branch._actions:
            for action in branch._actions[owner]['on_renaming']: 
                action(branch)
    
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
    
    
class Tree(TreeItem): pass
class Branch(TreeItem): pass




