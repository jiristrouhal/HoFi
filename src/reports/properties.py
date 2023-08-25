import core.tree as treemod
import tkinter as tk
import tkinter.ttk as ttk
from typing import Dict
from collections import OrderedDict


PROPERTIES_TITLE = "Properties"


class Properties:

    def __init__(self,master:tk.Tk|tk.Frame|ttk.Labelframe|None = None, label:str='Properties')->None:
        self.widget = ttk.Labelframe(master,text=PROPERTIES_TITLE)
        self.props:Dict[str,tk.Label] = OrderedDict()
        self.__configure_win()
        self.row = 0
        self.__label = label
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
        attr_values["name"]+= f" ({tag.lower()})"

        self.row = 0
        self.__draw_attributes(attr_values)
        self.__draw_attributes(dep_attr_values) 

    def __draw_attributes(self,attributes:Dict[str,treemod._Attribute])->None:
        for name, value in attributes.items():
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

