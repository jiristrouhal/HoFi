import tree as treemod
import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict
from collections import OrderedDict


class Properties:

    def __init__(self,master:tk.Tk|tk.Frame|ttk.Labelframe|None = None)->None:
        self.widget = tk.Frame(master)
        self.props:Dict[str,tk.Label] = OrderedDict()
        self.displayed_item:treemod.TreeItem|None = None
        self.__configure_win()

    def display(self,item:treemod.TreeItem)->None:
        self.__draw_properties(item.attributes)
        self.displayed_item = item

    def __draw_properties(self, properties:Dict[str,str])->None:
        row = 0
        for name, value in properties.items():
            label = tk.Label(self.widget,text=name+": "+value)
            self.props[name] = tk.Label(self.widget,text=name+": "+value)
            label.grid(row=row,sticky=tk.W)
            row += 1

    def clear(self)->None:
        self.displayed_item = None
        for child in self.widget.winfo_children(): child.destroy()
        self.props.clear()

    def __configure_win(self)->None:
        self.widget.pack(side=tk.LEFT)

