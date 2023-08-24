import tkinter.ttk as ttk
import tkinter as tk
import tkinter.messagebox as tkmsg
from typing import Tuple, Dict, Callable, List
from functools import partial
from collections import OrderedDict


import src.core.tree as treemod
import src.controls.right_click_menu as rcm


MENU_CMD_BRANCH_DELETE = "Delete"
MENU_CMD_BRANCH_EDIT = "Edit"
MENU_CMD_BRANCH_MOVE = "Move"
MENU_CMD_BRANCH_ADD = "Add"
MENU_CMD_BRANCH_OPEN_ALL = "Expand all"
MENU_CMD_BRANCH_CLOSE_ALL = "Collapse all"

BUTTON_OK = "OK"
BUTTON_CANCEL = "Cancel"
REVERT_ENTRY_VALUE_CHANGES = "Revert"


DELETE_BRANCH_WITH_CHILDREN_ERROR_TITLE = "Cannot delete item"
DELETE_BRANCH_WITH_CHILDREN_ERROR_CONTENT = ": Cannot delete item with children."


MOVE_WINDOW_TITLE = "Select new parent"


class TreeEditor:

    def __init__(self, parent:tk.Tk|tk.Toplevel|tk.Frame|tk.LabelFrame|None = None, label:str = "TreeEditor")->None:
        self.widget = ttk.Treeview(parent)
        self._bind_keys()
        self.__configure_widget()

        self._attribute_template:OrderedDict[str,treemod._Attribute] = OrderedDict()

        self._map:Dict[str,treemod.TreeItem] = dict()
        self.right_click_menu = rcm.RCMenu(self.widget)

        self.edit_window = tk.Toplevel(self.widget)
        self.edit_window.wm_withdraw()

        self.add_window = tk.Toplevel(self.widget)
        self.add_window.wm_withdraw()

        self.move_window = tk.Toplevel(self.widget)
        self.available_parents = ttk.Treeview(self.move_window)
        self.move_window.wm_withdraw()

        self.entries:Dict[str,tk.Entry] = dict()
        self.entry_options:Dict[str,Dict[str,ttk.Combobox]] = dict()
        # this flag will prevent some events to occur when the treeview is tested
        # WITHOUT opening the GUI (e.g. it prevents any message box from showing up)
        self._messageboxes_allowed:bool = True

        self._last_selection:Tuple[str,...] = ()
        self._on_selection:List[Callable[[treemod.TreeItem],None]] = list()
        self._on_unselection:List[Callable[[],None]] = list()
        self._on_edit:List[Callable[[treemod.TreeItem],None]] = list()
        self._on_any_modification:List[Callable[[treemod.TreeItem],None]] = list()
        self._on_tree_removal:List[Callable[[],None]] = list()
  
        self.label:str = label # an identifier used in actions of Tree Items

    def _bind_keys(self)->None:
        self.widget.bind("<Button-3>",self.right_click_item)
        self.widget.bind("<Double-Button-1>",self.open_edit_window_on_double_click,add="")
        self.widget.bind("<Key-Delete>",self.remove_selected_item)
        self.widget.bind("<<TreeviewSelect>>",self.check_selection_changes)

    def add_action_on_selection(self,action:Callable[[treemod.TreeItem],None])->None:
        if action not in self._on_selection:
            self._on_selection.append(action)

    def add_action_on_unselection(self,action:Callable[[],None])->None:
        if action not in self._on_unselection:
            self._on_unselection.append(action)
    
    def add_action_on_edit(self,action:Callable[[treemod.TreeItem],None])->None:
        if action not in self._on_edit:
            self._on_edit.append(action)

    def add_action_on_any_modification(self,action:Callable[[treemod.TreeItem],None])->None:
        if action not in self._on_any_modification:
            self._on_any_modification.append(action)

    def add_action_on_tree_removal(self,action:Callable[[],None])->None:
        if action not in self._on_tree_removal:
            self._on_tree_removal.append(action)

    def check_selection_changes(self,event:tk.Event|None=None)->None:
        current_selection = self.widget.selection()
        if current_selection==self._last_selection: return
        self._last_selection = current_selection
        if not current_selection: self.__no_item_selected()
        else: self.__new_item_selected(current_selection[0])

    def __new_item_selected(self,item_id:str)->None:
        item = self._map[item_id]
        for action in self._on_selection: action(item)

    def __no_item_selected(self)->None:
        for action in self._on_unselection: action()
        
    def __configure_widget(self)->None:
        style = ttk.Style()
        style.configure('Treeview',indent=15,rowheight=17)
        
        self.widget.pack(side=tk.RIGHT,expand=1,fill=tk.BOTH)
        scroll_y = ttk.Scrollbar(
            self.widget.master,
            orient=tk.VERTICAL,
            command=self.widget.yview)
        scroll_y.pack(side=tk.LEFT,fill=tk.Y)

        self.widget.config(
            selectmode='browse',
            show='tree', # hide zeroth row, that would contain the tree columns' headings
            yscrollcommand=scroll_y.set,
        )


    def remove_selected_item(self,event:tk.Event)->None: # pragma: no cover
        selection = self.widget.selection()
        if not selection: return
        item_iid = self.widget.selection()[0]
        if item_iid.strip()=="": return # cannot delete treeview root
        item = self._map[item_iid]
        if self.is_tree(item): return # cannot delete tree
        assert item.parent is not None
        item.parent.remove_child(item.name)
        
    @property
    def trees(self)->Tuple[str,...]: 
        return tuple([self._map[iid].name for iid in self.widget.get_children("")])

    def branch(self,treeview_iid:str)->treemod.TreeItem|None:
        if treeview_iid not in self._map: return None
        return self._map[treeview_iid]
    
    def _open_all(self,item_id:str)->None: # pragma: no cover
        self.widget.item(item_id,open=True)
        for child_id in self.widget.get_children(item_id): self._open_all(child_id)
    
    def _close_all(self,item_id:str)->None: # pragma: no cover
        self.widget.item(item_id,open=False)
        for child_id in self.widget.get_children(item_id): self._close_all(child_id)
    
    def load_tree(self,tree:treemod.Tree)->None: 
        if tree.name in self.trees: raise ValueError(f"The tree with {tree.name} is already present in the treeview.\n")
        # create action, that the tree object will run after it creates a new branch
        iid = str(id(tree)) 
        self.__load_item_into_tree(iid,tree)
        self._map[iid] = tree
        tree.add_data("treeview_iid",iid)
        tree.add_action(self.label,'add_child', partial(self._on_new_child,iid)) 
        tree.add_action(self.label,'on_self_rename', partial(self._on_renaming,iid))
        self._load_children(tree)
        self._open_all("")

    def __load_item_into_tree(self,iid:str,item:treemod.TreeItem)->None:
        parent_iid = "" if item.parent is None else item.parent.data["treeview_iid"]
        self.widget.insert(parent_iid,index=0,iid=iid,text=item.name)
        icon = treemod.tt.template(item.tag).icon_file
        if icon is not None: self.widget.item(iid,image=icon)

    def _load_children(self,parent:treemod.TreeItem)->None:
        for branch in parent._children:
            self.__insert_child_into_tree(branch)
            self._load_children(branch)

    def remove_tree(self,tree_id:str)->None:
        if tree_id not in self.widget.get_children(): 
            raise ValueError("Trying to delete nonexistent tree")
        for action in self._on_tree_removal:  action()
        self.__clear_related_actions(self._map[tree_id])
        self.widget.delete(tree_id)

    def __clear_related_actions(self,item:treemod.TreeItem):
        if self.label in item._actions: 
            item._actions[self.label].clear()
            item._actions.pop(self.label)
        for child in item._children: 
            self.__clear_related_actions(child)

    def __insert_child_into_tree(self, child:treemod.TreeItem)->None:
        item_iid = str(id(child))
        self._map[item_iid] = child
        self.__load_item_into_tree(item_iid,child)
        child.add_action(self.label,'add_child', partial(self._on_new_child, item_iid))
        child.add_action(self.label,'on_removal', partial(self._on_removal, item_iid))
        child.add_action(self.label,'on_renaming', partial(self._on_renaming, item_iid))
        child.add_action(self.label,'on_moving', partial(self._on_moving, item_iid))
        child.add_data("treeview_iid",item_iid)
        child.do_if_error_occurs(
            'cannot_remove_branch_with_children',
            self._cannot_remove_branch_with_children
        )

    def _on_new_child(self,parent_iid:str,new_branch:treemod.TreeItem)->None:
        child_iid = str(id(new_branch))
        self.__insert_child_into_tree(new_branch)
        # always open the item under which the new one has been added 
        self.widget.item(parent_iid,open=True)
        self.widget.selection_set(child_iid)
        # scroll to the added item
        self.widget.see(child_iid)

    def _on_removal(self,branch_iid:str,*args)->None:
        for action in self._on_any_modification: action(self._map[branch_iid])
        self._map.pop(branch_iid)
        self.widget.delete(branch_iid)

    def _on_renaming(self,item_iid:str,branch:treemod.TreeItem)->None:
        self.widget.item(item_iid,text=branch.name)

    def _on_moving(self,branch_iid:str,new_parent:treemod.TreeItem)->None:
        self.widget.move(branch_iid, new_parent.data["treeview_iid"], 0)


    def right_click_item(self,event:tk.Event)->None: # pragma: no cover
        item_id = self.widget.identify_row(event.y)
        if item_id.strip()=="": 
            return 
        if self.is_tree(self._map[item_id]): 
            self._open_right_click_menu(item_id,root=True)
        else: self._open_right_click_menu(item_id)
        if self.right_click_menu.winfo_exists():
            self.right_click_menu.tk_popup(x=event.x_root,y=event.y_root)
    
    def _open_right_click_menu(self,item_id:str,root:bool=False)->None:
        self.right_click_menu.destroy()
        if item_id.strip()=="": return
        self.right_click_menu = rcm.RCMenu(master=self.widget, tearoff=False)
        if not root: self.__add_commands_for_item(item_id)
        else: self.__add_commands_for_root(item_id)

    def __add_commands_for_root(self,root_id:str)->None:
        tree = self._map[root_id]
        self.right_click_menu.add_commands(
            {
                _define_add_cmd_label(tag): partial(self.open_add_window,root_id,tag) \
                for tag in tree.child_tags
            }
        )
        if tree.child_tags: self.right_click_menu.add_separator()
        self.right_click_menu.add_commands(
            {
                MENU_CMD_BRANCH_OPEN_ALL : partial(self._open_all,root_id),
                MENU_CMD_BRANCH_CLOSE_ALL :  partial(self._close_all,root_id)
            }
        )  

    def __add_commands_for_item(self,item_id:str)->None:
        branch:treemod.TreeItem = self._map[item_id]

        self.right_click_menu.add_commands(
            {
                _define_add_cmd_label(tag): partial(self.open_add_window,item_id,tag) \
                for tag in branch.child_tags
            }
        )
        if branch.child_tags: self.right_click_menu.add_separator()
        self.right_click_menu.add_commands(
            {
                MENU_CMD_BRANCH_EDIT : partial(self.open_edit_window,item_id),       
                MENU_CMD_BRANCH_MOVE : partial(self.open_move_window,item_id)
            }
        )
        if branch.parent is not None:
            self.right_click_menu.add_single_command(
                MENU_CMD_BRANCH_DELETE,
                partial(branch.parent.remove_child,branch.name)
            )
        if branch.user_defined_commands:
            self.right_click_menu.add_separator()
            self.right_click_menu.add_commands(
                {
                    label:command for label,command in branch.user_defined_commands.items()
                }
            )
        if self.widget.get_children(item_id):
            self.right_click_menu.add_separator()
            self.right_click_menu.add_commands(
                {
                    MENU_CMD_BRANCH_OPEN_ALL : partial(self._open_all,item_id),
                    MENU_CMD_BRANCH_CLOSE_ALL : partial(self._close_all,item_id)
                }
            )
        
    def open_add_window(self,parent_id:str,tag:str)->None:
        self.add_window = tk.Toplevel(self.widget)
        self.__configure_toplevel(self.add_window)
        self.__create_entries(self.add_window, treemod.tt.template(tag).attributes)
        
        self.add_window.bind("<Key-Escape>",self._disregard_add_entry_values_on_keypress)
        button_frame(
            self.add_window,
            ok_cmd = partial(self.confirm_add_entry_values,parent_id,tag),
            cancel_cmd = self.disregard_add_entry_values
        ).pack(side=tk.BOTTOM)

    def _disregard_add_entry_values_on_keypress(self,event:tk.Event)->None: # pragma: no cover
        self.disregard_add_entry_values()

    def confirm_add_entry_values(self,parent_id:str,tag:str)->None:
        attributes = treemod.tt.template(tag).attributes
        for label, entry in self.entries.items():
            attributes[label].set(entry.get())
        
        name = attributes.pop("name").value
        self._map[parent_id].new(name,tag=tag)
        new_child = self._map[parent_id]._children[-1]

        for attr_name in attributes:
            new_child.set_attribute(attr_name,attributes[attr_name].value)
            if attr_name in self.entry_options:
                for opt_label, option in self.entry_options[attr_name].items():
                    new_child.attributes[attr_name].choice_actions[opt_label](option.get())

        self.__clear_add_window_widgets()

        for action in self._on_any_modification: action(new_child)

    def disregard_add_entry_values(self)->None:
        self.__clear_add_window_widgets()

    def is_tree(self,item:treemod.TreeItem)->bool:
        return item.parent is None

    def open_edit_window_on_double_click(self,event:tk.Event)->None: # pragma: no cover
        iid = self.widget.identify_row(event.y)
        if iid.strip()=="": return 
        if self.is_tree(self._map[iid]): return
        # prevent automatic opening/closing of the element when double-clicked
        self.widget.item(iid,open=not self.widget.item(iid)["open"])
        self.open_edit_window(iid)

    def open_edit_window(self,item_id:str)->None:
        self.edit_window = tk.Toplevel(self.widget)
        self.__configure_toplevel(self.edit_window)
        item = self._map[item_id]
        if item.parent is None:
            self.__create_entries(self.edit_window, item.attributes, excluded=["name"])
        else:
            self.__create_entries(self.edit_window, item.attributes)
        self.edit_window.bind("<Key-Escape>",self.disregard_edit_entry_values_on_keypress)
        button_frame(
            self.edit_window,
            ok_cmd = partial(self.confirm_edit_entry_values,item_id),
            cancel_cmd = self.disregard_edit_entry_values,
            commands={REVERT_ENTRY_VALUE_CHANGES:partial(self.back_to_original_edit_entry_values,item_id)}
        ).pack(side=tk.BOTTOM)

    def back_to_original_edit_entry_values(self,branch_id:str)->None:
        for attribute, entry in self.entries.items():
            entry.delete(0,tk.END)
            entry.insert(0,self._map[branch_id].attributes[attribute].value)

    def confirm_edit_entry_values(self,item_id:str)->None:
        item = self._map[item_id]
        for attribute, entry in self.entries.items():
            if attribute=="name": 
                item.rename(entry.get())
            else:
                item.set_attribute(attribute, entry.get())

            if attribute in self.entry_options:
                for opt_label, option in self.entry_options[attribute].items():
                    attr = item.attributes[attribute]
                    attr.choice_actions[opt_label](option.get())

        # rename element in the tree
        self.widget.item(item_id,text=item.name)
        self.__clear_edit_window_widgets()
        for action in self._on_edit: action(item)
        for action in self._on_any_modification: action(item)
    
    def disregard_edit_entry_values_on_keypress(self,event:tk.Event)->None: # pragma: no cover
        self.__clear_edit_window_widgets()

    def disregard_edit_entry_values(self)->None:
        self.__clear_edit_window_widgets()

    def open_move_window(self,item_id:str)->None:
        # copy the treeview and throw away the moved item and its children
        self.move_window = tk.Toplevel(self.widget)
        self.__configure_toplevel(self.move_window)
        self.move_window.title(MOVE_WINDOW_TITLE)
        self.available_parents = ttk.Treeview(
            self.move_window, 
            show='tree', # hide zeroth row, that would contain the tree columns' headings
        )
        tree_id = self.__get_tree_id(item_id)

        if not item_id==tree_id:
            self.available_parents.insert("",index=0,iid=tree_id,text=self._map[tree_id].name,open=True)
            self._collect_available_parents(tree_id,item_id)

        self.available_parents.pack()
        parent = self._map[item_id].parent
        if parent is not None:
            self.available_parents.selection_set(parent.data["treeview_iid"])

        button_frame(
            self.move_window,
            ok_cmd = partial(self._confirm_parent_and_close_move_window,item_id),
            cancel_cmd = self._close_move_window
        ).pack(side=tk.BOTTOM)

    def _confirm_parent_and_close_move_window(self,item_id:str)->None:
        if not self.available_parents.winfo_exists(): return
        selection = self.available_parents.selection()
        if selection: # no parent was selected, thus keep the current one
            new_parent = self._map[selection[0]]
            branch = self._map[item_id]
            if branch._parent is not new_parent:
                branch._set_parent(new_parent)
                self.widget.move(item_id,selection[0],-1)
                for action in self._on_any_modification: action(branch)
                self.widget.see(item_id)

        self._close_move_window()


    def _close_move_window(self)->None:
        assert(self.move_window.winfo_exists() and self.available_parents.winfo_exists())
        self.move_window.destroy()

    def _collect_available_parents(self,parent_id:str,item_id:str):
        assert(self.available_parents.winfo_exists())
        for child_id in self.widget.get_children(parent_id):
            if child_id==item_id: continue
            # The potential parent's template must contain the tag of the moved item's template
            if not self._map[item_id].tag in self._map[child_id].child_tags: continue

            child = self.widget.item(child_id)
            self.available_parents.insert(parent_id,index=0,iid=child_id,text=child["text"],open=True)
            self._collect_available_parents(child_id,item_id)

    def _cannot_remove_branch_with_children(self,branch:treemod.TreeItem)->None: # pragma: no cover
        if not self._messageboxes_allowed: return
        tkmsg.showerror(
            DELETE_BRANCH_WITH_CHILDREN_ERROR_TITLE,
            branch.name+DELETE_BRANCH_WITH_CHILDREN_ERROR_CONTENT
        )

    def __clear_add_window_widgets(self)->None: # pragma: no cover
        self.add_window.destroy()
        self.entries.clear()
        self.entry_options.clear()

    def __clear_edit_window_widgets(self)->None: # pragma: no cover
        self.edit_window.destroy()
        self.entries.clear()
        self.entry_options.clear()

    def __create_entries(self,window:tk.Toplevel,attributes:Dict[str,treemod._Attribute],excluded:List[str]=[])->None:
        self.entries = dict()
        entries_frame = tk.Frame(window)
        row=0
        for key,attr in attributes.items():
            if key in excluded: continue
            col=0
            tk.Label(entries_frame,text=key).grid(row=row,column=col)
            col += 1
            if attr.options:
                box = ttk.Combobox(entries_frame,values=attr.options)
                box.insert(0, attr.formatted_value)
                box.current(attr.options.index(attr.formatted_value))
                box.grid(row=row,column=col)
                self.entries[key] = box
            else:
                vcmd = (entries_frame.register(attr.valid_entry),'%P')
                entry = tk.Entry(entries_frame, validate='key', validatecommand=vcmd)
                entry.insert(0, attr.value)
                entry.grid(row=row,column=col)
                self.entries[key] = entry

            if attr.choices:
                self.entry_options[key] = dict()
                for variable in attr.choices:
                    col += 1
                    tk.Label(entries_frame,text=' '+variable).grid(row=row, column=col)
                    box = ttk.Combobox(
                        entries_frame,
                        values=attr.choices[variable],
                        width=5
                    )
                    box.current(attr.choices[variable].index(attr.selected_choices[variable]))
                    self.entry_options[key][variable] = box
                    col += 1
                    box.grid(row=row, column=col)

            row += 1
        entries_frame.pack()

    def __configure_toplevel(self,toplevel:tk.Toplevel)->None:
        toplevel.grab_set()
        toplevel.focus_set()

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
    commands:Dict[str,Callable[[],None]] = {}
    )->tk.Frame:

    frame = tk.Frame(master)
    for name,cmd in commands.items():
        tk.Button(master=frame,text=name,command=cmd).pack(side=tk.RIGHT)
    tk.Button(master=frame,text=BUTTON_OK,command=ok_cmd).pack(side=tk.RIGHT)
    tk.Button(master=frame,text=BUTTON_CANCEL,command=cancel_cmd).pack(side=tk.RIGHT)
    return frame

def _define_add_cmd_label(tag:str)->str:
    return MENU_CMD_BRANCH_ADD+f" {tag.lower()}"