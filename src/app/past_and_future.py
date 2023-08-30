import datetime
from typing import Literal, Dict, Callable, Set
from functools import partial


class AlreadyRealized(Exception): pass
class AlreadyDismissed(Exception): pass
class DismissedEvent(Exception): pass
class EventStatusNotRecognized(Exception): pass


class ConfirmationNotRequired(Exception): pass


Action_Type = Literal['confirmed', 'dismissed']


class Event:

    def __init__(self, date:datetime.date, _reference_date:Callable[[],datetime.date] = datetime.date.today)->None:
        self.__date = date
        self.__reference_date = _reference_date
        self.__realized = self.__reference_date()>=date
        self.__actions:Dict[Action_Type, Dict[str, Callable]] = {
            'confirmed':{},
            'dismissed':{},
        }
        self.__dismissed = False
    
    @property
    def realized(self)->bool: return self.__realized
    @property
    def planned(self)->bool: return not (self.realized or self.dismissed)
    @property
    def dismissed(self)->bool: return self.__dismissed
    @property
    def confirmation_required(self)->bool:
        return self.planned and self.__date<=self.__reference_date()
    
    def add_action(self,on:Action_Type,owner:str, action:Callable[[],None])->None:
        if on not in self.__actions: raise KeyError
        else:
            if owner in self.__actions[on]: 
                raise KeyError(f"An action was already added with the owner name '{owner}'.")
            self.__actions[on][owner] = action
    
    def confirm_realization(self)->None:
        if self.realized:
            raise AlreadyRealized
        elif self.dismissed:
            raise AlreadyDismissed
        elif self.confirmation_required: 
            self.__realized = True
            for owner in self.__actions['confirmed']:
                self.__actions["confirmed"][owner]()
        else: 
            raise ConfirmationNotRequired
    
    def dismiss(self)->None:
        if self.realized:
            raise AlreadyRealized()
        elif self.dismissed:
            raise AlreadyDismissed()
        self.__dismissed = True
        for owner in self.__actions['dismissed']:
            self.__actions["dismissed"][owner]()
        
        
class Event_Manager:

    def __init__(self)->None:
        self.__realized:Set[Event] = set()
        self.__planned:Set[Event] = set()   
        self.__label:str = str(id(self))

    @property
    def realized(self)->Set[Event]: return self.__realized
    @property
    def planned(self)->Set[Event]: return self.__planned

    def add(self,event:Event)->None:
        if event.realized: 
            self.realized.add(event)
        elif event.planned: 
            self.planned.add(event)
            event.add_action('confirmed',self.__label, partial(self.__event_realized,event))
        else: 
            raise DismissedEvent("Dismissed events cant be added to an Event_Manager.")
        
    def __event_realized(self,event:Event)->None:
        self.realized.add(event)
        self.planned.remove(event)
 