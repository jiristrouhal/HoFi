
from typing import List, Dict, Callable, Any
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsg
import enum


import tree_to_xml as txml
import nlist
import tree as treemod
import naming



NAME_ALREADY_TAKEN_TITLE = "Name already exists"
NAME_ALREADY_TAKEN_MESSAGE_1 = "The trees with names "
NAME_ALREADY_TAKEN_MESSAGE_2 = " already exist. Use different names for the new or existing trees."


class ButtonID(enum.Enum):
    NEW_TREE = enum.auto()
    NEW_TREE_OK = enum.auto()
    NEW_TREE_CANCEL = enum.auto()


TREE_MANAGER_TITLE = "Tree Manager"
SET_NEW_TREE_NAME = "Set new tree name"
NAME_ENTRY_LABEL = "Name"


DEFAULT_TREE_NAME = "New"


BUTTONTEXT:Dict[ButtonID,str] = {
    ButtonID.NEW_TREE: "New",
    ButtonID.NEW_TREE_OK: "OK",
    ButtonID.NEW_TREE_CANCEL: "Cancel"
}


class Tree_Manager:

    def __init__(self,treelist:nlist.NamedItemsList,ui_master:tk.Frame|tk.Tk|None = None)->None:
        self.__converter = txml.Tree_XML_Converter()
        self.__treelist = treelist
        self.__treelist.add_name_warning(self.__warning_if_tree_names_already_taken)

        self.__ui = ttk.LabelFrame(master=ui_master,text=TREE_MANAGER_TITLE)
        self._buttons:Dict[ButtonID,tk.Button] = dict()
        self.__configure_ui()

        self._new_tree_window:tk.Toplevel|None = None
        self._tree_name_entry:tk.Entry|None = None

    @property
    def trees(self)->List[str]: return self.__treelist.names

    def __warning_if_tree_names_already_taken(self,*names:str)->None:
        tkmsg.showerror(
            NAME_ALREADY_TAKEN_TITLE, 
            NAME_ALREADY_TAKEN_MESSAGE_1+f"{names}"+NAME_ALREADY_TAKEN_MESSAGE_2
        )

    def __configure_ui(self)->None: # pragma: no cover
        self._buttons[ButtonID.NEW_TREE] = tk.Button(
            self.__ui,
            text=BUTTONTEXT[ButtonID.NEW_TREE],
            command=self.open_new_tree_window)
        self._buttons[ButtonID.NEW_TREE].pack(side=tk.LEFT)

    def __cleanup_new_tree_widgets(self)->None:
        if self._new_tree_window is not None:
            self._new_tree_window.destroy()
            self._new_tree_window = None
        if self._tree_name_entry is not None: 
            self._tree_name_entry.destroy()
            self._tree_name_entry = None

    def __add_button(
        self,
        master:tk.Frame|tk.Toplevel|tk.Tk,
        id:ButtonID,
        command:Callable[[],None]
        )->None:
        
        self._buttons[id] = tk.Button(master,text=BUTTONTEXT[id],command=command)

    def open_new_tree_window(self)->None: # pragma: no cover
        self.__cleanup_new_tree_widgets()
        self._new_tree_window = tk.Toplevel(self.__ui)
        self._new_tree_window.title(SET_NEW_TREE_NAME)
        self._tree_name_entry = tk.Entry(self._new_tree_window,width=50)
        self._tree_name_entry.insert(0,DEFAULT_TREE_NAME)
        self._tree_name_entry.pack()
        
        button_frame = tk.Frame(self._new_tree_window)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(button_frame,ButtonID.NEW_TREE_OK,self._confirm_new_tree_name)
        self.__add_button(button_frame,ButtonID.NEW_TREE_CANCEL,self.__close_new_tree_window)

    def _confirm_new_tree_name(self)->None:
        assert(self._tree_name_entry is not None)
        self.new(self._tree_name_entry.get())
        self.__close_new_tree_window()
        assert(self._tree_name_entry is None)

    def __close_new_tree_window(self)->None:
        if ButtonID.NEW_TREE_OK in self._buttons: self._buttons.pop(ButtonID.NEW_TREE_OK)
        if ButtonID.NEW_TREE_CANCEL in self._buttons: self._buttons.pop(ButtonID.NEW_TREE_CANCEL)
        self.__cleanup_new_tree_widgets()


    def new(self,name:str,tag:str=treemod.DEFAULT_TAG,attributes:Dict[str,Any]={})->None: 
        while self.__tree_name_is_taken(name):
            name = naming.change_name_if_already_taken(name)

        tree = treemod.Tree(name,tag=tag,attributes=attributes)
        self.__treelist.append(tree)

    def __tree_name_is_taken(self,name:str)->bool: 
        return name in self.trees
    