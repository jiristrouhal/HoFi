import tree as treemod
import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict
from collections import OrderedDict


class Properties:

    def __init__(self,master:tk.Tk|tk.Frame|ttk.Labelframe|None = None)->None:
        self.widget = tk.Frame(master)
        self.props:Dict[str,tk.Label] = OrderedDict()

    def display(self,item:treemod.TreeItem)->None:
        row = 0
        for attr_name, attr_value in item.attributes.items():
            label = tk.Label(self.widget,text=attr_name)
            value_widget = tk.Label(self.widget,text=attr_value)

            self.props[attr_name] = value_widget

            label.grid(row=row,column=0)
            value_widget.grid(row=row,column=1)
            row += 1



