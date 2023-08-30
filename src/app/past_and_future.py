import datetime
from typing import Callable, Dict, Literal


class AlreadyRealized(Exception): pass
class AlreadyDismissed(Exception): pass



Action_Type = Literal['confirmed', 'dismissed']
class Event:

    def __init__(self, date:datetime.date, _reference_date:Callable[[],datetime.date] = datetime.date.today)->None:
        self.__date = date
        self.__reference_date = _reference_date
        self.__realized = self.__reference_date()>=date
        self.__actions:Dict[Action_Type, Dict[str, Callable]] = {
            'confirmed':{},
            'dismissed':{}
        }
        self.__dismissed = False
    
    @property
    def realized(self)->bool: return self.__realized
    @property
    def planned(self)->bool: return not self.__realized and not self.__dismissed
    @property
    def dismissed(self)->bool: return self.__dismissed
    @property
    def confirmation_of_realization_is_required(self)->bool:
        return self.planned and self.__date>=self.__reference_date()
    
    def add_action(self,on:Action_Type,owner:str, action:Callable[[],None])->None:
        if on not in self.__actions: raise KeyError
        else:
            if owner in self.__actions[on]: 
                raise KeyError(f"An action was already added with the owner name '{owner}'.")
            self.__actions[on][owner] = action
    
    def confirm_realization(self)->None:
        if self.confirmation_of_realization_is_required: 
            self.__realized = True
            for owner in self.__actions['confirmed']:
                self.__actions["confirmed"][owner]()
        else:
            raise AlreadyRealized()
    
    def dismiss_realization(self)->None:
        if self.confirmation_of_realization_is_required: 
            self.__dismissed = True
            for owner in self.__actions['dismissed']:
                self.__actions["dismissed"][owner]()
        else:
            raise AlreadyDismissed()
        
        
    
        
            

        