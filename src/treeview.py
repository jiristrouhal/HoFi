import tkinter.ttk as ttk
import tkinter as tk
from typing import Tuple
import tree as treemod
from functools import partial


class Treeview:

    def __init__(self, parent:tk.Widget|None = None)->None:
        self._widget = ttk.Treeview(parent)

    @property
    def trees(self)->Tuple[str,...]: 
        return self._widget.get_children("")
    
    def add_tree(self,tree:treemod.Tree)->None: 
        if tree.name in self.trees: raise ValueError(f"The tree with {tree.name} is already present in the treeview.\n")
        # create action, that the tree object will run after it creates a new branch
        self._widget.insert("","end",iid=tree.name)
        tree.add_action('add_branch', partial(self._on_new_child,tree.name))

    def remove_tree(self,name:str)->None:
        if name not in self.trees: raise ValueError(f"Trying to delete nonexistent tree with name {name}.\n"
                                                    f"The existing tree names are {self.trees}\n")
        self._widget.delete(name)

    def _on_new_child(
        self,
        parent_iid:str,
        branch_parent:treemod.TWB,
        new_branch:treemod.TWB
        )->None:

        branch_iid = self._widget.insert(parent_iid,"end",text=new_branch.name)
        new_branch.add_action('add_branch', partial(self._on_new_child, branch_iid))
        new_branch.add_action('on_removal', partial(self._on_removal, branch_iid))
        new_branch.add_action('on_renaming', partial(self._on_renaming, branch_iid))

    def _on_removal(self,branch_iid:str,branch_parent:treemod.TWB, new_branch:treemod.TWB)->None:
        self._widget.delete(branch_iid)

    def _on_renaming(self,branch_iid:str,branch_parent:treemod.TWB, branch:treemod.TWB)->None:
        self._widget.item(branch_iid,text=branch.name)
