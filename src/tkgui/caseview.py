import tkinter.ttk as ttk
import tkinter as tk
from functools import partial

from src.core.editor import Case_View, Item, Lang_Object
from typing import List, Tuple, Callable, Dict, Any
from typing import Optional
from PIL import Image, ImageTk
import os

class Case_View_Tk(Case_View):
    
    def __init__(
        self, 
        window:tk.Tk|tk.Frame, 
        root_item:Item, 
        attrs_for_display:Dict[str,Tuple[str,...]] = {},
        lang:Lang_Object = Lang_Object.get_lang_object(),
        icons:Dict[str,str] = {}
        )->None:
        
        self.__tree:ttk.Treeview = ttk.Treeview(window)
        self.__icons = {label:self.__get_icon(path) for label,path in icons.items()}
        for label, icon in self.__icons.items(): 
            if icon is None: self.__icons.pop(label)
        yscrollbar = ttk.Scrollbar(window, orient ="vertical", command = self.__tree.yview)
        yscrollbar.pack(anchor=tk.W, fill=tk.Y, side=tk.LEFT)
        self.__tree.configure(yscrollcommand=yscrollbar, height=25)

        self.__id = str(id(self))
        self.__lang = lang

        self.__tree['columns'] = list(attrs_for_display.keys())
        self.__attrs_for_display = attrs_for_display
        self.__precision:int = 28
        self.__trailing_zeros:bool = False
        self.__use_thousands_separator:bool = False

        root_item.add_action(self.__id, 'adopt', self.__new_item_under_root)
        root_item.add_action(self.__id, 'leave', self.__remove_item)
        root_item.add_action(self.__id, 'rename', self.__rename_item)
        root_item.add_action_on_set(self.__id, self.__set_displayed_values_of_item_attributes)

        self.__item_dict:Dict[str,Item] = {"":root_item}

        self.__set_up_headings()
        self.__reversed_sort:bool = False

    @property
    def id(self)->str: return self.__id
    @property
    def widget(self)->ttk.Treeview: return self.__tree

    def bind(self, sequence:str, action:Callable[[tk.Event], None])->None:
        self.__tree.bind(sequence, action)

    def configure(self, **kwargs) -> None:
        for label, arg in kwargs.items():
            match label:
                case "precision": self.__precision = arg
                case "trailing_zeros": self.__trailing_zeros = arg
                case "use_thousands_separator": self.__use_thousands_separator = arg
                case _: continue

    def do_on_tree_item(self, action:Callable[[Item, tk.Event],None])->Callable[[tk.Event], None]:
        def item_action(event:tk.Event)->None:
            tree_item_iid = self.__tree.identify_row(event.y)
            item = self.__item_dict[tree_item_iid]
            return action(item, event)
        return item_action

    def __new_item(self, item:Item)->None:
        values = self.__collect_and_set_values(item)
        item_iid = self.__tree.insert(
            item.parent.id, 
            index=tk.END, 
            iid=item.id, 
            text=item.name, 
            values=values,
        )
        if item.itype in self.__icons: self.__tree.item(item_iid, image=self.__icons[item.itype])
        
        self.__tree.see(item.id)
        item.add_action(self.__id, 'adopt', self.__new_item)
        item.add_action(self.__id, 'leave', self.__remove_item)
        item.add_action(self.__id, 'rename', self.__rename_item)
        item.add_action_on_set(self.__id, self.__set_displayed_values_of_item_attributes)
        self.__item_dict[item.id] = item

        for child in item.children: self.__new_item(child)

    def __new_item_under_root(self, item:Item)->None:
        values = self.__collect_and_set_values(item)
        self.__tree.insert("", index=tk.END, iid=item.id, text=item.name, values=values)
        item.add_action(self.__id, 'adopt', self.__new_item)
        item.add_action(self.__id, 'leave', self.__remove_item)
        item.add_action(self.__id, 'rename', self.__rename_item)
        item.add_action_on_set(self.__id, self.__set_displayed_values_of_item_attributes)
        self.__item_dict[item.id] = item

        for child in item.children: self.__new_item(child)

    def __get_icon(self, path:str)->Optional[ImageTk.PhotoImage]:
        if os.path.isfile(path):
            return ImageTk.PhotoImage(Image.open(path))
        else: 
            return None

    def __remove_item(self, item:Item)->None:
        for child in item.children: self.__remove_item(child)
        self.__tree.delete(item.id)
        item.remove_action(self.__id, 'adopt')
        item.remove_action(self.__id, 'leave')
        item.remove_action(self.__id, 'rename')
        item.remove_action_on_set(self.__id)
        self.__item_dict.pop(item.id)

    def __rename_item(self, item:Item)->None:
        self.__tree.item(item.id, text=item.name)

    def __set_displayed_values_of_item_attributes(self, item:Item)->None:
        values = self.__collect_and_set_values(item)
        self.__tree.item(item.id, values=values)

    def __collect_and_set_values(self, item:Item)->List[str]:
        values:List[str] = list()
        for label_group in self.__attrs_for_display:
            values.append("")
            for label in self.__attrs_for_display[label_group]:
                if item.has_attribute(label): 
                    attr = item.attribute(label)
                    print_args:Dict[str, Any] = dict()
                    if attr.type=="real" or attr.type=="quantity":
                        print_args["precision"] = self.__precision
                        print_args["trailing_zeros"] = self.__trailing_zeros
                    elif attr.type=="money":
                        print_args["use_thousands_separator"] = self.__use_thousands_separator
                    values[-1] = str(item.attribute(label).print(**print_args))
                    break
        return values
    
    def __set_up_headings(self)->None:
        heading_labels = list(self.__tree['columns'])
        for heading_label in heading_labels:
            self.__tree.heading(
                heading_label, 
                text = self.__lang("Item_Attributes", heading_label),
                command = partial(self.__sort_all_by, heading_label),
                anchor=tk.CENTER,
            )
            self.__tree.column(heading_label, anchor=tk.E, minwidth=50, width=100)
        self.__tree.heading(
            '#0', 
            text=self.__lang("Item_Attributes", "name"), 
            command = partial(self.__sort_all_by, '#0'),
            anchor=tk.CENTER
        )
        self.__tree.column('#0', minwidth=100, width=300)

    def __sort_all_by(self,column_label:str)->None:
        self.__sort_by(column_label, parent_iid="")
        self.__reversed_sort = not self.__reversed_sort

    def __sort_by(self, column_label:str, parent_iid:str)->None:
        if column_label=="#0":
            child_data = [(c, self.__tree.item(c)['text']) for c in self.__tree.get_children(parent_iid)]
        else:
            child_data = [(c, self.__tree.set(c, column_label)) for c in self.__tree.get_children(parent_iid)]
        child_data.sort(key=lambda x: x[1], reverse=self.__reversed_sort)
        for index, (c, _) in enumerate(child_data):
            self.__tree.move(c, parent_iid, index)

        for c in self.__tree.get_children(parent_iid):
            self.__sort_by(column_label=column_label, parent_iid=c)
        

