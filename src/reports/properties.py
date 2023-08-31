import core.tree as treemod
import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict, Tuple
from collections import OrderedDict


class Properties:

    def __init__(
        self,
        master:tk.Tk|tk.Frame|ttk.Labelframe|None = None, 
        label:str='Properties', 
        title:str='Properties',
        name_attr:str = "name",
        ignored:Tuple[str,...] = ()
        )->None:

        self.widget = ttk.Labelframe(master,text=title)
        self.props:Dict[str,tk.Label] = OrderedDict()
        self.__configure_win()
        self.row = 0
        self.__label = label
        self.name_attr = name_attr
        self.ignored = ignored
    @property
    def label(self)->str: return self.__label

    def display(self,item:treemod.TreeItem)->None:
        self.clear()
        self.__draw_properties(
            item.attributes, 
            item.dependent_attributes,
            item.tag)
        self.displayed_item = item

    def __draw_properties(
        self, 
        attributes:Dict[str,treemod._Attribute], 
        dependent_attributes:Dict[str,treemod.Dependent_Attr],
        tag:str=""
        )->None:

        attr_values = {label:x.formatted_value for label,x in attributes.items()}
        dep_attr_values = {label:x.formatted_value for label,x in dependent_attributes.items()}
        attr_values[self.name_attr]+= f" ({tag.lower()})"

        self.row = 0
        self.__draw_attributes(attr_values)
        self.__draw_attributes(dep_attr_values) 

    def __draw_attributes(self,attributes:Dict[str,treemod._Attribute])->None:
        for name, value in attributes.items():
            
            if name in self.ignored: continue

            label = tk.Label(self.widget,text="• "+ name+": ")
            value_widget = tk.Label(self.widget,text=str(value))
            self.props[name] = value_widget
            label.grid(row=self.row,column=0,sticky=tk.W,padx=(15,0))
            value_widget.grid(row=self.row,column=1,sticky=tk.W,padx=(0,15))
            self.row += 1

    def clear(self)->None:
        for child in self.widget.winfo_children(): child.destroy()
        self.props.clear()

    def __configure_win(self)->None:
        self.widget.pack(side=tk.LEFT,expand=1,fill=tk.BOTH,ipady=10)

