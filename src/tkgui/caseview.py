import tkinter.ttk as ttk
import tkinter as tk

from src.core.editor import Case_View, Item
from typing import List, Tuple, Callable, Dict

class Case_View_Tk(Case_View):
    
    def __init__(self, window:tk.Tk|tk.Frame, root_item:Item, *attrs_for_display:str)->None:
        self.__tree:ttk.Treeview = ttk.Treeview(window)
        self.__id = str(id(self))

        self.__tree['columns'] = attrs_for_display
        self.__attrs_for_display = attrs_for_display

        root_item.add_action(self.__id, 'adopt', self.__new_item_under_root)
        root_item.add_action(self.__id, 'leave', self.__remove_item)
        root_item.add_action(self.__id, 'rename', self.__rename_item)
        root_item.add_action_on_set(self.__id, self.__set_displayed_values_of_item_attributes)

        self.__item_dict:Dict[str,Item] = {"":root_item}

    @property
    def id(self)->str: return self.__id
    @property
    def widget(self)->ttk.Treeview: return self.__tree

    def bind(self, sequence:str, action:Callable[[tk.Event], None])->None:
        self.__tree.bind(sequence, action)

    def do_on_tree_item(self, action:Callable[[Item, tk.Event],None])->Callable[[tk.Event], None]:
        def item_action(event:tk.Event)->None:
            tree_item_iid = self.__tree.identify_row(event.y)
            item = self.__item_dict[tree_item_iid]
            return action(item, event)
        return item_action

    def __new_item(self, item:Item)->None:
        values = self.__collect_and_set_values(item)
        self.__tree.insert(item.parent.id, index=tk.END, iid=item.id, text=item.name, values=values)
        self.__tree.see(item.id)
        item.add_action(self.__id, 'adopt', self.__new_item)
        item.add_action(self.__id, 'leave', self.__remove_item)
        item.add_action(self.__id, 'rename', self.__rename_item)
        item.add_action_on_set(self.__id, self.__set_displayed_values_of_item_attributes)
        self.__item_dict[item.id] = item

    def __new_item_under_root(self, item:Item)->None:
        values = self.__collect_and_set_values(item)
        self.__tree.insert("", index=tk.END, iid=item.id, text=item.name, values=values)
        item.add_action(self.__id, 'adopt', self.__new_item)
        item.add_action(self.__id, 'leave', self.__remove_item)
        item.add_action(self.__id, 'rename', self.__rename_item)
        item.add_action_on_set(self.__id, self.__set_displayed_values_of_item_attributes)
        self.__item_dict[item.id] = item

    def __remove_item(self, item:Item)->None:
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

    def __collect_and_set_values(self, item:Item)->Tuple[str,...]:
        values:List[str] = list()
        for label in self.__attrs_for_display:
            if item.has_attribute(label): 
                values.append(str(item.attribute(label).print()))
            else:
                values.append("")
        return tuple(values)