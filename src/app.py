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

    @property
    def branches(self)->List[str]: return [b.name for b in self.__branches]


@dataclasses.dataclass
class Branch:
    name:str
    weight:int
    length:int


def read_tree_data(path:str)->et.ElementTree:
    return et.parse(path)

