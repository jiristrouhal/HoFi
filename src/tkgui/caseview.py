import tkinter.ttk as ttk
import tkinter as tk

from src.core.editor import Case_View


class Case_View_Tk(Case_View):
    
    def __init__(self, root:tk.Tk|tk.Frame)->None:
        self.__root = root
        self.__widget = ttk.Treeview(root)
    
    @property
    def widget(self)->ttk.Treeview: return self.__widget