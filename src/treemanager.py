
from typing import List, Dict, Callable, Any, Literal
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsg
import enum
from functools import partial


import tree_to_xml as txml
import nlist
import tree as treemod
import naming



NAME_ALREADY_TAKEN_TITLE = "Name already exists"
NAME_ALREADY_TAKEN_MESSAGE_1 = "A tree with the name "
NAME_ALREADY_TAKEN_MESSAGE_2 = " already exists. Use different name."


TREE_MANAGER_TITLE = "Tree Manager"
SET_NEW_TREE_NAME = "Set new tree name"
RENAME_TREE = "Rename tree"
NAME_ENTRY_LABEL = "Name"

DEFAULT_TREE_NAME = "New"


class ButtonID(enum.Enum):
    NEW_TREE = enum.auto()
    NEW_TREE_OK = enum.auto()
    NEW_TREE_CANCEL = enum.auto()
    RENAME_TREE = enum.auto()
    RENAME_TREE_OK = enum.auto()
    RENAME_TREE_CANCEL = enum.auto()



BUTTONTEXT:Dict[ButtonID,str] = {
    ButtonID.NEW_TREE: "New",
    ButtonID.NEW_TREE_OK: "OK",
    ButtonID.NEW_TREE_CANCEL: "Cancel",
    ButtonID.RENAME_TREE: "Rename",
    ButtonID.RENAME_TREE_OK: "OK",
    ButtonID.RENAME_TREE_CANCEL: "Cancel",
}


class Tree_Manager:

    def __init__(self,treelist:nlist.NamedItemsList,ui_master:tk.Frame|tk.Tk|None = None, )->None:
        self.__converter = txml.Tree_XML_Converter()
        self.__ui = ttk.LabelFrame(master=ui_master,text=TREE_MANAGER_TITLE)
        self._buttons:Dict[ButtonID,tk.Button] = dict()
        self._view = ttk.Treeview(self.__ui, selectmode='browse')
        self._iid_to_tree_map:Dict[str,treemod.Tree] = dict()
        self._window_new:tk.Toplevel|None = None
        self._entry_name:tk.Entry|None = None
        self._window_rename:tk.Toplevel|None = None
        self.__configure_ui()
        
        self.__treelist = treelist
        self.__treelist.add_name_warning(self.__error_if_tree_names_already_taken)
        self.__treelist.add_action_on_adding(self.__add_tree_to_view)
        # this flag will prevent some events to occur when the treeview is tested
        # WITHOUT opening the GUI (e.g. it prevents any message box from showing up)
        self._messageboxes_allowed:bool = True

    @property
    def trees(self)->List[str]: return self.__treelist.names

    def __error_if_tree_names_already_taken(self,name:str)->None:  # pragma: no cover
        if self._messageboxes_allowed:
            tkmsg.showerror(
                NAME_ALREADY_TAKEN_TITLE, 
                NAME_ALREADY_TAKEN_MESSAGE_1+f"{name}"+NAME_ALREADY_TAKEN_MESSAGE_2
            )

    def __configure_ui(self)->None: # pragma: no cover
        button_frame = tk.Frame(self.__ui)
        self.__add_button(
            button_frame,
            ButtonID.NEW_TREE,
            command=self.open_new_tree_window,
            side='left')
        self.__add_button(
            button_frame,
            ButtonID.RENAME_TREE,
            command=self._open_rename_window_for_selected_tree,
            side='left')
        button_frame.pack()

        scroll_y = ttk.Scrollbar(self._view.master,orient=tk.VERTICAL,command=self._view.yview)
        scroll_y.pack(side=tk.LEFT,fill=tk.Y)

        self._view.config(
            selectmode='browse',
            show='tree', # hide zeroth row, that would contain the tree columns' headings
            yscrollcommand=scroll_y.set,
        )
        self._view.pack(side=tk.BOTTOM,expand=1,fill=tk.X)

    def __cleanup_new_tree_widgets(self)->None:
        if self._window_new is not None:
            self._window_new.destroy()
            self._window_new = None
        if self._entry_name is not None: 
            self._entry_name.destroy()
            self._entry_name = None

    def __cleanup_rename_tree_widgets(self)->None:
        if self._window_rename is not None:
            self._window_rename.destroy()
            self._window_rename = None
        if self._entry_name is not None: 
            self._entry_name.destroy()
            self._entry_name = None

    def __add_button(
        self, 
        master: tk.Frame, 
        id:ButtonID, 
        command:Callable[[],None], 
        side:Literal['left','right','top','bottom']
        )->None:
        
        self._buttons[id] = tk.Button(master,text=BUTTONTEXT[id],command=command)
        self._buttons[id].pack(side=side)

    def _open_rename_window_for_selected_tree(self)->None:
        if not self._view.selection(): return
        tree = self._iid_to_tree_map[self._view.selection()[0]]
        self._open_rename_tree_window(tree)

    def _open_rename_tree_window(self,tree:treemod.Tree)->None: # pragma: no cover
        self.__cleanup_rename_tree_widgets()
        self._window_rename = tk.Toplevel(self.__ui)
        self._window_rename.title(RENAME_TREE)
        self._entry_name = tk.Entry(self._window_new,width=50)
        self._entry_name.pack()
        self._entry_name.insert(0,tree.name)

        button_frame = tk.Frame(self._window_new)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(button_frame,ButtonID.RENAME_TREE_OK,partial(self._confirm_rename,tree),side='left')
        self.__add_button(button_frame,ButtonID.RENAME_TREE_CANCEL,self._close_rename_tree_window,side='left')
        
    def open_new_tree_window(self)->None: # pragma: no cover
        self.__cleanup_new_tree_widgets()
        self._window_new = tk.Toplevel(self.__ui)
        self._window_new.title(SET_NEW_TREE_NAME)
        self._entry_name = tk.Entry(self._window_new,width=50)
        self._entry_name.insert(0,DEFAULT_TREE_NAME)
        self._entry_name.pack()
        
        button_frame = tk.Frame(self._window_new)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(button_frame,ButtonID.NEW_TREE_OK,self._confirm_new_tree_name,side='left')
        self.__add_button(button_frame,ButtonID.NEW_TREE_CANCEL,self.__close_new_tree_window,side='left')

    def _confirm_rename(self,tree:treemod.Tree)->None:
        assert(self._entry_name is not None)
        new_name = self._entry_name.get()
        if self.tree_exists(new_name) and self.get_tree(new_name) is not tree: 
            self.__error_if_tree_names_already_taken(new_name)
            return 
        tree.rename(self._entry_name.get())
        self._close_rename_tree_window()

    def _close_rename_tree_window(self)->None:
        if ButtonID.RENAME_TREE_OK in self._buttons: 
            self._buttons.pop(ButtonID.RENAME_TREE_OK)
        if ButtonID.RENAME_TREE_CANCEL in self._buttons: 
            self._buttons.pop(ButtonID.RENAME_TREE_CANCEL)
        self.__cleanup_rename_tree_widgets()

    def _confirm_new_tree_name(self)->None:
        assert(self._entry_name is not None)
        self.new(self._entry_name.get())
        self.__close_new_tree_window()
        assert(self._entry_name is None)

    def __close_new_tree_window(self)->None:
        if ButtonID.NEW_TREE_OK in self._buttons: 
            self._buttons.pop(ButtonID.NEW_TREE_OK)
        if ButtonID.NEW_TREE_CANCEL in self._buttons: 
            self._buttons.pop(ButtonID.NEW_TREE_CANCEL)
        self.__cleanup_new_tree_widgets()

    def new(self,name:str,tag:str=treemod.DEFAULT_TAG,attributes:Dict[str,Any]={})->None: 
        tree = treemod.Tree(name,tag=tag,attributes=attributes)
        self.__treelist.append(tree)

    def __add_tree_to_view(self,tree:treemod.Tree)->None:
        tree_iid = self._view.insert("",0,text=tree.name)
        self._iid_to_tree_map[tree_iid] = tree

    def get_tree(self,name:str)->treemod.Tree|None:
        return self.__treelist.item(name)

    def rename(self,old_name:str,new_name:str)->None:
        tree_to_be_renamed= self.get_tree(old_name)
        if tree_to_be_renamed is None: return
        tree_to_be_renamed.rename(new_name)

    def tree_exists(self,name:str)->bool: 
        return name in self.trees
    