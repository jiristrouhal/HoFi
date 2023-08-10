import tree_to_xml as txml
from typing import List, Dict, Callable
import naming
import tkinter as tk
import tkinter.ttk as ttk
import enum


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

    def __init__(self,ui_master:tk.Frame|tk.Tk|None = None)->None:
        self.__converter = txml.Tree_XML_Converter()
        self.ui = ttk.LabelFrame(master=ui_master,text=TREE_MANAGER_TITLE)
        self.buttons:Dict[ButtonID,tk.Button] = dict()
        self.__configure_ui()
        self.new_tree_window:tk.Toplevel|None = None
        self.tree_name_entry:tk.Entry|None = None

    @property
    def trees(self)->List[str]: return self.__converter.trees

    def __configure_ui(self)->None: # pragma: no cover
        self.buttons[ButtonID.NEW_TREE] = tk.Button(
            self.ui,
            text=BUTTONTEXT[ButtonID.NEW_TREE],
            command=self.open_new_tree_window)
        self.buttons[ButtonID.NEW_TREE].pack(side=tk.LEFT)

    def __cleanup_new_tree_widgets(self)->None:
        if self.new_tree_window is not None:
            self.new_tree_window.destroy()
            self.new_tree_window = None
        if self.tree_name_entry is not None: 
            self.tree_name_entry.destroy()
            self.tree_name_entry = None

    def __add_button(
        self,
        master:tk.Frame|tk.Toplevel|tk.Tk,
        id:ButtonID,
        command:Callable[[],None]
        )->None:
        
        self.buttons[id] = tk.Button(master,text=BUTTONTEXT[id],command=command)

    def open_new_tree_window(self)->None: # pragma: no cover
        self.__cleanup_new_tree_widgets()
        self.new_tree_window = tk.Toplevel(self.ui)
        self.new_tree_window.title(SET_NEW_TREE_NAME)
        self.tree_name_entry = tk.Entry(self.new_tree_window,width=50)
        self.tree_name_entry.insert(0,DEFAULT_TREE_NAME)
        self.tree_name_entry.pack()
        
        button_frame = tk.Frame(self.new_tree_window)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(button_frame,ButtonID.NEW_TREE_OK,self._confirm_new_tree_name)
        self.__add_button(button_frame,ButtonID.NEW_TREE_CANCEL,self.__close_new_tree_window)

    def _confirm_new_tree_name(self)->None:
        assert(self.tree_name_entry is not None)
        self.new(self.tree_name_entry.get())
        self.__close_new_tree_window()
        assert(self.tree_name_entry is None)

    def __close_new_tree_window(self)->None:
        if ButtonID.NEW_TREE_OK in self.buttons: self.buttons.pop(ButtonID.NEW_TREE_OK)
        if ButtonID.NEW_TREE_CANCEL in self.buttons: self.buttons.pop(ButtonID.NEW_TREE_CANCEL)
        self.__cleanup_new_tree_widgets()


    def new(self,name:str)->None: 
        while self.__tree_name_is_taken(name):
            name = naming.change_name_if_already_taken(name)
        self.__converter.new_tree(name)

    def __tree_name_is_taken(self,name:str)->bool: 
        return name in self.trees
    