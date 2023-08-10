import tree_to_xml as txml
from typing import List
import naming
import tkinter as tk


class Tree_Manager:

    def __init__(self,ui_master:tk.Frame|tk.Tk|None = None)->None:
        self.__converter = txml.Tree_XML_Converter()
        self.ui = tk.Frame(master=ui_master)
        self.__configure_ui()

    @property
    def trees(self)->List[str]: return self.__converter.trees

    def __configure_ui(self)->None: # pragma: no cover
        pass

    def new(self,name:str)->None: 
        while self.__tree_name_is_taken(name):
            name = naming.change_name_if_already_taken(name)
        self.__converter.new_tree(name)

    def __tree_name_is_taken(self,name:str)->bool: return name in self.trees
    