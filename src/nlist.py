from typing import List, Protocol, Callable, Tuple


class _NItem(Protocol):

    @property
    def name(self)->str: ...


class NamedItemsList:

    def __init__(self)->None:
        self.__items:List[_NItem] = list()
        self.__name_warnings:List[Callable[[str],None]] = list()

    def append(self,*items:_NItem)->None: 
        already_taken_names:List[str] = list()
        for item in items: 
            if self.item(item.name) is None: 
                self.__items.append(item)
            else:
                already_taken_names.append(item.name)
        if already_taken_names:
            for warning in self.__name_warnings:
                warning(*already_taken_names)
            
    def item(self,name:str)->_NItem|None:
        for item in self.__items:
            if name==item.name: return item
        return None

    def remove(self,name:str)->None:
        item = self.item(name)
        if item is None: return
        self.__items.remove(item)

    def add_name_warning(self,warning_action:Callable[[str],None]):
        self.__name_warnings.append(warning_action)

    @property
    def names(self)->List[str]: return [i.name for i in self.__items]
    

    

    

    