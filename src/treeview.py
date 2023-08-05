import tkinter.ttk as ttk
import tkinter as tk
from typing import Tuple, Dict
import tree as treemod
from functools import partial


class Treeview:

    def __init__(self, parent:tk.Widget|None = None)->None:
        self._widget = ttk.Treeview(parent)
        self._widget.bind("<Button-3>",self._open_right_click_menu)
        self._map:Dict[str,treemod.Branch] = dict()

    @property
    def trees(self)->Tuple[str,...]: 
        return self._widget.get_children("")
    
    def branch(self,treeview_iid:str)->treemod.Branch|None:
        if treeview_iid not in self._map: return None
        return self._map[treeview_iid]
    
    def add_tree_to_widget(self,tree:treemod.Tree)->None: 
        if tree.name in self.trees: raise ValueError(f"The tree with {tree.name} is already present in the treeview.\n")
        # create action, that the tree object will run after it creates a new branch
        self._widget.insert("","end",iid=tree.name)
        tree.add_data("treeview_iid",tree.name)
        tree.add_action('add_branch', partial(self._on_new_child,tree.name))

    def remove_tree(self,name:str)->None:
        if name not in self.trees: raise ValueError(f"Trying to delete nonexistent tree with name {name}.\n"
                                                    f"The existing tree names are {self.trees}\n")
        self._widget.delete(name)

    def _on_new_child(
        self,
        parent_iid:str,
        new_branch:treemod.TWB
        )->None:

        branch_iid = self._widget.insert(parent_iid,"end",text=new_branch.name)
        self._map[branch_iid] = new_branch

        new_branch.add_action('add_branch', partial(self._on_new_child, branch_iid))
        new_branch.add_action('on_removal', partial(self._on_removal, branch_iid))
        new_branch.add_action('on_renaming', partial(self._on_renaming, branch_iid))
        new_branch.add_action('on_moving', partial(self._on_moving, branch_iid))
        new_branch.add_data("treeview_iid",branch_iid)


    def _on_removal(self,branch_iid:str,*args)->None:
        self._map.pop(branch_iid)
        self._widget.delete(branch_iid)

    def _on_renaming(self,branch_iid:str,branch:treemod.TWB)->None:
        self._widget.item(branch_iid,text=branch.name)

    def _on_moving(self,branch_iid:str,new_parent:treemod.TWB)->None:
        self._widget.move(branch_iid, new_parent.data["treeview_iid"], -1)
 
    @staticmethod
    def _open_right_click_menu(event:tk.Event)->None:
        pass
