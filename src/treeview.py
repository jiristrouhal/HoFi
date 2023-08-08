


import tkinter.ttk as ttk
import tkinter as tk
import tkinter.messagebox as tkmsg
from typing import Tuple, Dict, Callable, Any
import src.tree as treemod
from functools import partial


MENU_CMD_BRANCH_DELETE = "Delete"
MENU_CMD_BRANCH_EDIT = "Edit"
MENU_CMD_BRANCH_MOVE = "Move"
MENU_CMD_BRANCH_ADD = "Add new"

BUTTON_OK = "OK"
BUTTON_CANCEL = "Cancel"


DELETE_BRANCH_WITH_CHILDREN_ERROR_TITLE = "Cannot delete item"
DELETE_BRANCH_WITH_CHILDREN_ERROR_CONTENT = ": Cannot delete item with children."


MOVE_WINDOW_TITLE = "Select new parent"


def configure_treeview(treeview:ttk.Treeview)->None:
    # hide zeroth row, that would contain the tree columns' headings
    treeview.config(
        selectmode='browse',
        show='tree'
    )


class Treeview:

    def __init__(self, parent:tk.Tk|tk.Toplevel|tk.Frame|None = None)->None:
        self.widget = ttk.Treeview(parent)
        self.__configure_widget()

        self._attribute_template = {"name":"New", "lenght":"0"}

        self._map:Dict[str,treemod.TWB] = dict()
        self.right_click_menu:tk.Menu|None = None

        self.edit_window:tk.Toplevel|None = None
        self.edit_entries:Dict[str,tk.Entry] = dict()

        self.add_window:tk.Toplevel|None = None
        self.add_window_entries:Dict[str,tk.Entry] = dict()
        
        self.move_window:tk.Toplevel|None = None
        self.available_parents:ttk.Treeview|None = None

        # this flag will prevent some events to occur when the treeview is tested
        # WITHOUT opening the GUI (e.g. it prevents any message box from showing up)
        self._messageboxes_allowed:bool = False
        
    def __configure_widget(self)->None:
        self.widget.bind("<Button-3>",self.right_click_item)
        self.widget.bind("<Double-Button-1>",self.open_edit_window_on_double_click,add="")

        configure_treeview(self.widget)

        self.widget.pack()

    @property
    def trees(self)->Tuple[str,...]: 
        return self.widget.get_children("")
    
    def branch(self,treeview_iid:str)->treemod.TWB|None:
        if treeview_iid not in self._map: return None
        return self._map[treeview_iid]
    
    def load_tree(self,tree:treemod.Tree)->None: 
        if tree.name in self.trees: raise ValueError(f"The tree with {tree.name} is already present in the treeview.\n")
        # create action, that the tree object will run after it creates a new branch
        self.widget.insert("","end",iid=tree.name,text=tree.name)
        self._map[tree.name] = tree
        tree.add_data("treeview_iid",tree.name)
        tree.add_action('add_branch', partial(self._on_new_child,tree.name)) 
        self._load_branches(tree)

    def _load_branches(self,parent:treemod.TWB)->None:
        for branch in parent._branches:
            iid = self.widget.insert(parent.data["treeview_iid"],"end",text=branch.name)
            self._map[iid] = branch
            branch.add_action('add_branch', partial(self._on_new_child, iid))
            branch.add_action('on_removal', partial(self._on_removal, iid))
            branch.add_action('on_renaming', partial(self._on_renaming, iid))
            branch.add_action('on_moving', partial(self._on_moving, iid))
            branch.add_data("treeview_iid",iid)

            branch.do_if_error_occurs(
                'cannot_remove_branch_with_children',
                self._cannot_remove_branch_with_children
            )
            self._load_branches(branch)
        

    def remove_tree(self,name:str)->None:
        if name not in self.trees: raise ValueError(f"Trying to delete nonexistent tree with name {name}.\n"
                                                    f"The existing tree names are {self.trees}\n")
        self.widget.delete(name)

    def _on_new_child(
        self,
        parent_iid:str,
        new_branch:treemod.TWB
        )->None:

        branch_iid = self.widget.insert(parent_iid,"end",text=new_branch.name)
        self._map[branch_iid] = new_branch
        new_branch.add_action('add_branch', partial(self._on_new_child, branch_iid))
        new_branch.add_action('on_removal', partial(self._on_removal, branch_iid))
        new_branch.add_action('on_renaming', partial(self._on_renaming, branch_iid))
        new_branch.add_action('on_moving', partial(self._on_moving, branch_iid))
        new_branch.add_data("treeview_iid",branch_iid)

        new_branch.do_if_error_occurs(
            'cannot_remove_branch_with_children',
            self._cannot_remove_branch_with_children
        )
        # always open the item under which the new one has been added 
        self.widget.item(parent_iid,open=True)
    
    def _cannot_remove_branch_with_children(self,branch:treemod.TWB)->None: # pragma: no cover
        if not self._messageboxes_allowed: return
        tkmsg.showerror(
            DELETE_BRANCH_WITH_CHILDREN_ERROR_TITLE,
            branch.name+DELETE_BRANCH_WITH_CHILDREN_ERROR_CONTENT
        )

    def _on_removal(self,branch_iid:str,*args)->None:
        self._map.pop(branch_iid)
        self.widget.delete(branch_iid)

    def _on_renaming(self,branch_iid:str,branch:treemod.TWB)->None:
        self.widget.item(branch_iid,text=branch.name)

    def _on_moving(self,branch_iid:str,new_parent:treemod.TWB)->None:
        self.widget.move(branch_iid, new_parent.data["treeview_iid"], -1)


    def right_click_item(self,event:tk.Event)->None: # pragma: no cover
        item_id = self.widget.identify_row(event.y)
        if item_id.strip()=="": return 

        if self._map[item_id].parent is None: 
            self._open_right_click_menu(item_id,root=True)
        else: self._open_right_click_menu(item_id)
        if self.right_click_menu is not None:
            self.right_click_menu.tk_popup(x=event.x_root,y=event.y_root)
    
    def _open_right_click_menu(self,item_id:str,root:bool=False)->None:
        if self.right_click_menu is not None: 
            self.right_click_menu.destroy()
            self.right_click_menu = None
        if item_id.strip()=="": return
        self.right_click_menu = tk.Menu(master=self.widget, tearoff=False)
        if not root: self.__add_commands_for_item(item_id)
        else: self.__add_commands_for_root(item_id)

    def __add_commands_for_root(self,root_id:str)->None:
        if self.right_click_menu is None: return
        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_ADD,
            command=self._right_click_menu_command(
                partial(
                    self.open_add_window,
                    root_id,
                    self._attribute_template,
                )
            )
        )
        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_EDIT,
            command=self._right_click_menu_command(partial(self.open_edit_window,root_id)))

    def __add_commands_for_item(self,item_id:str)->None:
        branch:treemod.TWB = self._map[item_id]
        if self.right_click_menu is None: return
        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_ADD,
            command=self._right_click_menu_command(
                partial(
                    self.open_add_window,
                    item_id,
                    self._attribute_template
                )
            )
        )
        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_EDIT,
            command=self._right_click_menu_command(partial(self.open_edit_window,item_id)))
        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_MOVE,
            command=self._right_click_menu_command(partial(self.open_move_window,item_id))
        )
        self.right_click_menu.add_separator()
        assert(branch.parent is not None)
        self.right_click_menu.add_command(
            label=MENU_CMD_BRANCH_DELETE,
            command=self._right_click_menu_command(partial(branch.parent.remove_branch,branch.name)))
        
    def _right_click_menu_command(self,cmd:Callable)->Callable:
        def menu_cmd(*args,**kwargs): 
            cmd(*args,**kwargs)
            self.right_click_menu.destroy()
            self.right_click_menu = None
        return menu_cmd
    
    def open_add_window(self,parent_id:str,attributes:Dict[str,Any])->None:
        self.add_window = tk.Toplevel(self.widget)
        self.add_window.grab_set()
        self.add_window_entries = dict()
        entries_frame = tk.Frame(self.add_window)
        row=0
        for key,value in attributes.items():
            tk.Label(entries_frame,text=key).grid(row=row,column=0)
            entry = tk.Entry(entries_frame)
            entry.insert(0,value)
            entry.grid(row=row,column=1)
            self.add_window_entries[key] = entry
            row += 1
        entries_frame.pack()

        assert(self.add_window is not None)
        button_frame(
            self.add_window,
            ok_cmd = partial(self.confirm_add_entry_values,parent_id),
            cancel_cmd = self.disregard_add_entry_values
        ).pack(side=tk.BOTTOM)

    def confirm_add_entry_values(self,parent_id:str)->None:
        if self.add_window is None: return
        attributes = dict()

        for label, entry in self.add_window_entries.items():
            attributes[label] = entry.get()
        
        name = attributes.pop("name")
        self._map[parent_id].add_branch(name,attributes)

        self.add_window.destroy()
        self.add_window = None
        for entry_name in self.add_window_entries: 
            self.add_window_entries[entry_name].destroy()
        self.add_window_entries.clear()

    def disregard_add_entry_values(self)->None:
        if self.add_window is None: return
        self.add_window.destroy()
        self.add_window = None
        for entry_name in self.add_window_entries: 
            self.add_window_entries[entry_name].destroy()
        self.add_window_entries.clear()

    def open_edit_window_on_double_click(self,event:tk.Event)->None: # pragma: no cover
        iid = self.widget.identify_row(event.y)
        if iid.strip()=="": return
        # prevent automatic opening/closing of the element when double-clicked
        self.widget.item(iid,open=not self.widget.item(iid)["open"])
        self.open_edit_window(iid)

    def open_edit_window(self,item_id:str)->None:
        self.edit_window = tk.Toplevel(self.widget)
        self.edit_window.grab_set()
        self.edit_window.focus_get()
        self.edit_entries = dict()
        item = self._map[item_id]
        entries_frame = tk.Frame(self.edit_window)
        row = 0
        for key,value in item.attributes.items(): 
            tk.Label(entries_frame,text=key).grid(row=row,column=0)
            entry = tk.Entry(entries_frame)
            entry.insert(0,value)
            entry.grid(row=row,column=1)
            self.edit_entries[key] = entry
            row += 1
        entries_frame.pack()
        
        assert(self.edit_window is not None)
        button_frame(
            self.edit_window,
            ok_cmd = partial(self.confirm_edit_entry_values,item_id),
            cancel_cmd = self.disregard_edit_entry_values,
            revert_cmd = partial(self.back_to_original_edit_entry_values,item_id)
        ).pack(side=tk.BOTTOM)
        

    def back_to_original_edit_entry_values(self,branch_id:str)->None:
        if self.edit_window is None: return
        for attribute, entry in self.edit_entries.items():
            entry.delete(0,tk.END)
            entry.insert(0,self._map[branch_id].attributes[attribute])

    def confirm_edit_entry_values(self,branch_id:str)->None:
        if self.edit_window is None: return
        for attribute, entry in self.edit_entries.items():
            self._map[branch_id].set_attribute(attribute, entry.get())
        # rename element in the tree
        self.widget.item(branch_id,text=self.edit_entries["name"].get())

        self.edit_window.destroy()
        self.edit_window = None
        for entry_name in self.edit_entries: self.edit_entries[entry_name].destroy()
        self.edit_entries.clear()

    def disregard_edit_entry_values(self)->None:
        if self.edit_window is None: return
        self.edit_window.destroy()
        self.edit_window = None
        for entry_name in self.edit_entries: self.edit_entries[entry_name].destroy()
        self.edit_entries.clear()

    def open_move_window(self,item_id:str)->None:
        # copy the treeview and throw away the moved item and its children
        assert(self.move_window is None and self.available_parents is None)

        self.move_window = tk.Toplevel(self.widget)
        self.move_window.grab_set()
        self.move_window.title(MOVE_WINDOW_TITLE)

        self.available_parents = ttk.Treeview(self.move_window)
        configure_treeview(self.available_parents)
        tree_id = self.__get_tree_id(item_id)
        self.available_parents.insert("","end",iid=tree_id,text=tree_id)
        self._collect_available_parents(tree_id,item_id)
        self.available_parents.pack()
        button_frame(
            self.move_window,
            ok_cmd = partial(self._confirm_parent_and_close_move_window,item_id),
            cancel_cmd = self._close_move_window
        ).pack(side=tk.BOTTOM)

    def _confirm_parent_and_close_move_window(self,item_id:str)->None:
        if self.available_parents is None: return
        selection = self.available_parents.selection()
        if not selection: return #empty selection
        branch = self._map[item_id]
        branch._set_parent(self._map[selection[0]])
        self.widget.move(item_id,selection[0],-1)
        self._close_move_window()

    def _close_move_window(self)->None:
        assert(self.move_window is not None and self.available_parents is not None)
        self.move_window.destroy()
        self.move_window = None
        self.available_parents = None

    def _collect_available_parents(self,parent_id:str,item_id:str):
        assert(self.available_parents is not None)
        for child_id in self.widget.get_children(parent_id):
            if child_id==item_id: continue
            child = self.widget.item(child_id)
            self.available_parents.insert(parent_id,"end",iid=child_id,text=child["text"])
            self._collect_available_parents(child_id,item_id)

    def __get_tree_id(self,item_id:str)->str:
        id = item_id
        while not id=="":
            tree_id = id
            id = self.widget.parent(tree_id)
        return str(tree_id)


def button_frame(
    master:tk.Toplevel|tk.Tk,
    ok_cmd:Callable[[],None],
    cancel_cmd:Callable[[],None],
    **commands:Callable[[],None]
    )->tk.Frame:

    frame = tk.Frame(master)
    for name,cmd in commands.items():
        tk.Button(master=frame,text=name,command=cmd).pack(side=tk.RIGHT)
    tk.Button(master=frame,text=BUTTON_OK,command=ok_cmd).pack(side=tk.RIGHT)
    tk.Button(master=frame,text=BUTTON_CANCEL,command=cancel_cmd).pack(side=tk.RIGHT)
    return frame