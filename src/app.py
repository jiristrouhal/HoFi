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
        return [b.name for b in self._branches]
    
    def add_branch(self,branch:Branch)->None:
        self._branches.append(branch)

    def remove_branch(self,branch_name:str)->Branch|None:
        branch = self._find_branch(branch_name)
        if branch is not None: self._branches.remove(branch)
        return branch
    
    def _find_branch(self,branch_name:str)->Branch|None:
        for b in self._branches:
            if b.name==branch_name: return b
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

