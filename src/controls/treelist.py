from typing import List, Callable, Set
import core.naming
from core.tree import Tree


class TreeList:

    def __init__(self,label:str="")->None:
        self.__items:List[Tree] = list()
        self.__name_warnings:List[Callable[[str],None]] = list()

        self.__on_removal:List[Callable[[Tree],None]] = list()
        self.__on_adding:List[Callable[[Tree],None]] = list()
        self.__on_renaming:List[Callable[[Tree],None]] = list()

        self.label:str = str(id(self)) if label.strip()=="" else label
        self._modified_trees:Set[Tree] = set()

    @property
    def names(self)->List[str]: return [i.name for i in self.__items]

    def add_action_on_removal(self,action:Callable[[Tree],None])->None:
        self.__on_removal.append(action)

    def add_action_on_adding(self,action:Callable[[Tree],None])->None:
        self.__on_adding.append(action)

    def add_action_on_renaming(self,action:Callable[[Tree],None])->None:
        self.__on_renaming.append(action)

    def append(self,item:Tree)->None: 
        self.__items.append(item)
        # adjust the tree name after appending to list
        self.__adjust_tree_name(item) 
        for action in self.__on_renaming:
            item.add_action(self.label,'on_self_rename',action)

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
        if item in self._modified_trees:
            self._modified_trees.remove(item)

    def rename(self,old_name:str,new_name:str)->Tree|None:
        item = self.item(old_name)
        if item is not None: 
            item.rename(new_name)
            self.__adjust_tree_name(item)
        return item
    
    def add_tree_to_modified(self,tree:Tree)->None:
        self._modified_trees.add(tree)

    def add_name_warning(self,warning_action:Callable[[str],None]):
        self.__name_warnings.append(warning_action)

    def __adjust_tree_name(self,item:Tree)->None:
        name = core.naming.strip_and_join_spaces(item.name)
        names = self.names
        names.remove(name)  # prevent item having name collision with itself
        while name in names:
            name = core.naming.change_name_if_already_taken(name)
        item.rename(name)

    

    