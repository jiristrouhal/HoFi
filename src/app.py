from __future__ import annotations
import tkinter
from tkinter.ttk import Treeview
import xml.etree.ElementTree as et
from typing import List



import dataclasses


class Tree:

    def __init__(self)->None:
        self.__branches:List[Branch] = list()
    
    def add_branch(self,branch:Branch)->None:
        self.__branches.append(branch)

    def remove_branch(self,branch_name:str)->Branch|None:
        branch = self._find_branch(branch_name)
        if branch is not None: self.__branches.remove(branch)
        return branch

    def _find_branch(self,branch_name:str)->Branch|None:
        for b in self.__branches:
            if b.name==branch_name: return b
        return None

    @property
    def branches(self)->List[str]: return [b.name for b in self.__branches]


@dataclasses.dataclass
class Branch:
    name:str
    weight:int
    length:int


def read_tree_data(path:str)->et.ElementTree:
    return et.parse(path)

