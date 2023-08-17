import tree as treemod
import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict
from collections import OrderedDict


PROPERTIES_TITLE = "Properties"


class Properties:

    def __init__(self,master:tk.Tk|tk.Frame|ttk.Labelframe|None = None)->None:
        self.widget = ttk.Labelframe(master,text=PROPERTIES_TITLE)
        self.props:Dict[str,tk.Label] = OrderedDict()
        self.displayed_item:treemod.TreeItem|None = None
        self.__configure_win()

    def display(self,item:treemod.TreeItem)->None:
        if self.displayed_item != item:
            self.clear()
            self.__draw_properties(item.attributes, item.tag)
            self.displayed_item = item

    def redraw(self, x)->None:
        if self.displayed_item is not None:
            item = self.displayed_item
            self.clear()
            self.displayed_item = item
            self.__draw_properties(
                self.displayed_item.attributes, 
                self.displayed_item.tag
            )

    def __draw_properties(self, properties:Dict[str,str], tag:str="")->None:
        row = 0
        if tag.strip()!="": 
            properties["name"] += f" ({tag.lower()})"
        for name, value in properties.items():
            label = tk.Label(self.widget,text="• "+ name+": ")
            value_widget = tk.Label(self.widget,text=value)
            self.props[name] = value_widget
            label.grid(row=row,column=0,sticky=tk.W,padx=(15,0))
            value_widget.grid(row=row,column=1,sticky=tk.W,padx=(0,15))
            row += 1

    def clear(self)->None:
        self.displayed_item = None
        for child in self.widget.winfo_children(): child.destroy()
        self.props.clear()

    def __configure_win(self)->None:
        self.widget.pack(side=tk.LEFT,expand=1,fill=tk.BOTH,ipady=10)

