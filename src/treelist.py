from typing import List, Callable
import naming
from tree import Tree
from functools import partial


class TreeList:

    def __init__(self)->None:
        self.__items:List[Tree] = list()
        self.__name_warnings:List[Callable[[str],None]] = list()

        self.__on_removal:List[Callable[[Tree],None]] = list()
        self.__on_adding:List[Callable[[Tree],None]] = list()
        self.__on_renaming:List[Callable[[Tree],None]] = list()

    @property
    def names(self)->List[str]: return [i.name for i in self.__items]

    def add_action_on_removal(self,action:Callable[[Tree],None])->None:
        self.__on_removal.append(action)

    def add_action_on_adding(self,action:Callable[[Tree],None])->None:
        self.__on_adding.append(action)

    def add_action_on_renaming(self,action:Callable[[Tree],None])->None:
        self.__on_renaming.append(action)

    def append(self,item:Tree)->None: 
        name = item.name
        names = self.names
        while name in names:
            name = naming.change_name_if_already_taken(name)
        item.rename(name)
        self.__items.append(item)
        for action in self.__on_adding: action(item)
            
    def item(self,name:str)->Tree|None:
        for item in self.__items:
            if name==item.name: return item
        return None

    def remove(self,item_name:str)->None:
        item = self.item(item_name)
        if item is None: return
        for action in self.__on_removal: action(item)
        self.__items.remove(item)

    def rename(self,old_name:str,new_name:str)->None:
        item = self.item(old_name)
        if item is None: return
        item.rename(new_name)
        for action in self.__on_renaming: action(item)

    def add_name_warning(self,warning_action:Callable[[str],None]):
        self.__name_warnings.append(warning_action)


    

    