from __future__ import annotations
import tkinter
from tkinter.ttk import Treeview
import xml.etree.ElementTree as et
from typing import List
import abc



class Thing_With_Branches(abc.ABC):

    def __init__(self)->None:
        self._branches:List[Branch] = list()

    def branches(self,*branches_along_the_path:str)->List[str]: 
        if branches_along_the_path:
            # list branches growing out of some child element of the current object
            smallest_parent_branch = self._find_branch(*branches_along_the_path)
            if smallest_parent_branch is not None:
                return smallest_parent_branch.branches()
        # display branches growint out of the current object (branch, tree, ...)
        return [b.name for b in self._branches]
    
    def add_branch(self,branch:Branch,*branches_along_the_path:str)->None:
        if branches_along_the_path:
            # add the new branch to some sub-branch
            smallest_parent_branch = self._find_branch(*branches_along_the_path)
            if smallest_parent_branch is not None:
                smallest_parent_branch._branches.append(branch)
        # add the branch directly to the current object
        else:
            self._branches.append(branch)

    def remove_branch(self,branch_name:str)->Branch|None:
        branch = self._find_branch(branch_name)
        if branch is not None:
            # delete the branch only, when no other grows out of it 
            if len(branch._branches)==0: self._branches.remove(branch)
        return branch
    
    def _find_branch(self,*branch_names:str)->Branch|None:
        parent_name = branch_names[0]
        for b in self._branches:
            if parent_name==b.name:
                if len(branch_names)>1:
                    return b._find_branch(*branch_names[1:])
                elif len(branch_names)==1:
                    return b
                else: # This case happend if no branch name is provided originally
                    return None
        return None
    
    
class Tree(Thing_With_Branches):
    
    pass


class Branch(Thing_With_Branches):

    def __init__(self,name:str,weight:int,length:int)->None:
        self.name = name
        self.weight = weight
        self.length = length
        super().__init__()



def read_tree_data(path:str)->et.ElementTree:
    return et.parse(path)

