from typing import List, Protocol, Callable
import naming


class _NItem(Protocol):

    @property
    def name(self)->str: # pragma: no cover
        ...  

    def rename(self,new_name:str)->None: # pragma: no cover
        ... 
class NamedItemsList:

    def __init__(self)->None:
        self.__items:List[_NItem] = list()
        self.__name_warnings:List[Callable[[str],None]] = list()

        self.__on_removal:List[Callable[[_NItem],None]] = list()
        self.__on_adding:List[Callable[[_NItem],None]] = list()

    @property
    def names(self)->List[str]: return [i.name for i in self.__items]

    def add_action_on_removal(self,action:Callable[[_NItem],None])->None:
        self.__on_removal.append(action)

    def add_action_on_adding(self,action:Callable[[_NItem],None])->None:
        self.__on_adding.append(action)

    def append(self,item:_NItem)->None: 
        name = item.name
        names = self.names
        while name in names:
            name = naming.change_name_if_already_taken(name)
        item.rename(name)
        self.__items.append(item)
        for action in self.__on_adding: action(item)
            
    def item(self,name:str)->_NItem|None:
        for item in self.__items:
            if name==item.name: return item
        return None

    def remove(self,item_name:str)->None:
        item = self.item(item_name)
        if item is None: return
        self.__items.remove(item)
        for action in self.__on_removal: action(item)

    def add_name_warning(self,warning_action:Callable[[str],None]):
        self.__name_warnings.append(warning_action)


    

    