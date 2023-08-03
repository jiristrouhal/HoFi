import tkinter.ttk as ttk
import tkinter as tk
from typing import Tuple
import tree as treemod


class Treeview:

    def __init__(self, parent:tk.Widget|None = None)->None:
        self.__widget = ttk.Treeview(parent)

    @property
    def trees(self)->Tuple[str,...]: 
        return self.__widget.get_children("")
    
    def add_tree(self,tree:treemod.Tree)->None: 
        if tree.name in self.trees: raise ValueError(f"The tree with {tree.name} is already present in the treeview.\n")
        self.__widget.insert("","end",iid=tree.name)

    def remove_tree(self,name:str)->None:
        if name not in self.trees: raise ValueError(f"Trying to delete nonexistent tree with name {name}.\n"
                                                    f"The existing tree names are {self.trees}\n")
        self.__widget.delete(name)