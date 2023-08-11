from typing import List, Protocol, Callable


class _NItem(Protocol):

    @property
    def name(self)->str: ...


class NamedItemsList:

    def __init__(self)->None:
        self.__items:List[_NItem] = list()
        self.__name_warnings:List[Callable[[str],None]] = list()
        self.__selection:List[str] = list()

        self.__on_removal:List[Callable[[str],None]] = list()
        self.__on_adding:List[Callable[[str],None]] = list()
        self.__on_selecting:List[Callable[[str],None]] = list()
        self.__on_deselecting:List[Callable[[str],None]] = list()

    @property
    def selected_names(self)->List[str]: return self.__selection
    
    def add_action_on_removal(self,action:Callable[[str],None])->None:
        self.__on_removal.append(action)

    def add_action_on_adding(self,action:Callable[[str],None])->None:
        self.__on_adding.append(action)

    def add_action_on_selecting(self,action:Callable[[str],None])->None:
        self.__on_selecting.append(action)

    def add_action_on_deselecting(self,action:Callable[[str],None])->None:
        self.__on_deselecting.append(action)

    def append(self,*items:_NItem)->None: 
        already_taken_names:List[str] = list()
        for item in items: 
            if self.item(item.name) is None: 
                self.__items.append(item)
                for action in self.__on_adding: action(item.name)
            else:
                already_taken_names.append(item.name)
        if already_taken_names:
            for warning in self.__name_warnings:
                warning(*already_taken_names)
            
    def item(self,name:str)->_NItem|None:
        for item in self.__items:
            if name==item.name: return item
        return None
    
    def select(self,name:str)->None:
        if name not in self.names: return
        self.__selection.append(name)

    def deselect(self,name:str)->None:
        if name not in self.__selection: return
        self.__selection.remove(name)

    def remove(self,name:str)->None:
        item = self.item(name)
        if item is None: return
        self.__items.remove(item)
        for action in self.__on_removal: action(name)

    def add_name_warning(self,warning_action:Callable[[str],None]):
        self.__name_warnings.append(warning_action)

    @property
    def names(self)->List[str]: return [i.name for i in self.__items]
    

    

    

    