import tkinter.ttk as ttk
import tkinter as tk
from typing import Tuple, Dict, Callable
import tree as treemod
from functools import partial


MENU_CMD_BRANCH_DELETE = "Delete"
MENU_CMD_BRANCH_EDIT = "Edit"

class Treeview:

    def __init__(self, parent:tk.Widget|None = None)->None:
        self._widget = ttk.Treeview(parent)
        self._widget.bind("<Button-3>",self.right_click_item)
        self._map:Dict[str,treemod.Branch] = dict()
        self.right_click_menu:tk.Menu|None = None
        self.edit_window:tk.Toplevel|None = None
        self.edit_entries:Dict[str,tk.Entry] = dict()

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


    def right_click_item(self,event:tk.Event)->None:
        item_id = self._widget.identify_row(event.y)
        if item_id.strip()=="": return 
        self._open_right_click_menu_for_item(item_id)

    def _right_click_menu_command(self,cmd:Callable)->Callable:
        def menu_cmd(*args,**kwargs): 
            cmd(*args,**kwargs)
            self.right_click_menu.destroy()
            self.right_click_menu = None
        return menu_cmd
    
    def _open_right_click_menu_for_item(self,item_id:str)->None:
        branch = self._map[item_id]
        self.right_click_menu = tk.Menu(master=self._widget, tearoff=False)

        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_EDIT,
            command=self._right_click_menu_command(partial(self.open_edit_window,item_id)))
        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_DELETE,
            command=self._right_click_menu_command(partial(branch.parent.remove_branch,branch.name)))

    def open_edit_window(self,branch_id:str)->None:
        self.edit_window = tk.Toplevel(self._widget)
        self.edit_entries = dict()
        branch = self._map[branch_id]
        row = 0
        for key,value in branch.attributes.items(): 
            label = tk.Label(self.edit_window,text=key)
            label.grid(row=row,column=0)
            entry = tk.Entry(self.edit_window)
            entry.insert(0,value)
            entry.grid(row=row,column=1)
            self.edit_entries[key] = entry

    def confirm_edit_entry_values(self,branch_id:str)->None:
        if self.edit_window is None: return
        for attribute, entry in self.edit_entries.items():
            self._map[branch_id].set_attribute(attribute, entry.get())

        self.edit_window.destroy()
        self.edit_window = None

    def _set_entry(self,entry_key:str,new_value:str)->None:
        if entry_key not in self.edit_entries: return
        self.edit_entries[entry_key].delete(0,"end")
        self.edit_entries[entry_key].insert(0,new_value)



            
