from __future__ import annotations
from typing import List, Tuple, Dict, Any, Callable, Literal
import abc
import src.naming


class TreeItem(abc.ABC):

    def __init__(self,name:str="",attributes:Dict[str,Any]=dict())->None:
        self._attributes = {k:str(v) for k,v in attributes.items()} 
        self._attributes["name"] = name.strip()
        self._branches:List[TreeItem] = list()
        self._parent:TreeItem|None = None
        self._actions:Dict[str,List[Callable]] = \
        {
            'add_branch':[], 
            'on_removal':[], 
            'on_renaming':[],
            'on_moving':[]
        }
        self._do_on_error:Dict[str,List[Callable]] = {
            'cannot_remove_branch_with_children':[],
        }
        self._data:Dict[str,Any] = dict()
    @property
    def name(self)->str: return self._attributes["name"]
    @property
    def attributes(self)->Dict[str,str]: return self._attributes.copy()
    @property 
    def parent(self)->TreeItem|None: return self._parent
    @property
    def data(self)->Dict[str,Any]: return self._data.copy()

    def add_action(
        self,
        on:Literal['add_branch','on_removal','on_renaming','on_moving'],
        action:Callable[[TreeItem],None]
        )->None: 

        self._actions[on].append(action)

    def add_data(self,new_key:str,value:Any)->None:
        if new_key in self._data: 
            raise KeyError(
                f"Branch/tree {self.name}: Cannot add value to already existing key ({new_key})."
            )
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
            self._parent._branches.remove(self)
        # if the name already exists under the new parent, change the current name
        while new_parent._find_branch(self.name) is not None: 
            self._attributes["name"] = src.naming.change_name_if_already_taken(self.name)
        self._parent = new_parent
        self._parent._branches.append(self)

    def rename(self,name:str)->None:
        if self._parent is not None:
            if self._parent._find_branch(name) is not None:
                name = src.naming.change_name_if_already_taken(name)
        self._attributes["name"] = name.strip()

    def branches(self,*branches_along_the_path:str)->List[str]: 
        if branches_along_the_path:
            # list branches growing out of some child element of the current object
            lowest_level_branch = self._find_branch(*branches_along_the_path)
            if lowest_level_branch is not None:
                return lowest_level_branch.branches()
        # display branches growint out of the current object (branch, tree, ...)
        return [b.name for b in self._branches]
    
    def add_branch(self,name:str,attributes:Dict[str,Any]=dict(),*branches_along_the_path:str)->None:
        if branches_along_the_path:
            # add the new branch to some sub-branch
            smallest_parent_branch = self._find_branch(*branches_along_the_path)
            if smallest_parent_branch is None: return
            smallest_parent_branch.add_branch(name,attributes)
        else:  # add the branch directly to the current object
            branch = Branch(name,attributes)
            branch._set_parent(self)
            for action in self._actions['add_branch']: 
                action(branch)
        
    def move_branch(self,branch_path:Tuple[str,...],new_branch_parent_path:Tuple[str,...])->None:
        if self._does_path_point_to_child_of_branch_or_to_branch_itself(branch_path,new_branch_parent_path):
            return
        branch = self._find_branch(*branch_path)
        if branch is not None:
            if len(new_branch_parent_path)==0: branch._set_parent(self)
            else:
                parent = self._find_branch(*new_branch_parent_path)
                if parent is not None: branch._set_parent(parent)

            for action in branch._actions['on_moving']: 
                action(parent)

    def remove_branch(self,*branch_path:str)->None:
        if len(branch_path)>1:
            parent_branch = self._find_branch(*branch_path[:-1])
            if parent_branch is not None: 
                parent_branch.remove_branch(*branch_path[1:])

        branch_to_be_removed = self._find_branch(branch_path[-1])
        if branch_to_be_removed is None: return

        if branch_to_be_removed.branches(): 
            for action in branch_to_be_removed._do_on_error['cannot_remove_branch_with_children']: 
                action(branch_to_be_removed)
            return

        for action in branch_to_be_removed._actions['on_removal']: 
            action(branch_to_be_removed)
        self._branches.remove(branch_to_be_removed)
    
    def rename_branch(self,branch_path:Tuple[str,...],new_name:str)->None:
        branch = self._find_branch(*branch_path)
        if branch is None: return
        branch.rename(new_name)
        for action in branch._actions['on_renaming']: 
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
    
    def _find_branch(self,*branch_names:str)->TreeItem|None:
        if not branch_names: return None
        parent_name = branch_names[0]
        for branch in self._branches:
            if parent_name==branch.name:
                if len(branch_names)>1: 
                    return branch._find_branch(*branch_names[1:])
                return branch
        return None
    
    
class Tree(TreeItem): pass
class Branch(TreeItem): pass




