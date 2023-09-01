import sys
sys.path.insert(1, "src")


from functools import partial
from typing import Callable, Dict, Literal


from src.controls.tree_editor import TreeEditor
import src.events.past_and_future as pf
import src.core.tree as treemod


Event_Change_Type = Literal['realized_to_planned', 'planned_to_realized']
class TreeEventConnector:

    def __init__(
        self, 
        editor:TreeEditor, 
        event_manager:pf.Event_Manager, 
        date_label:str,
        )->None:

        event_manager_id = str(id(event_manager))
        self.editor = editor

        self.editor.add_action(event_manager_id, 'load_tree', self._new_tree_item_events)
        self.label = str(id(self))
        self.date_label = date_label
        self.event_manager = event_manager
        self._actions:Dict[Event_Change_Type,Dict[str,Callable[[],None]]] = {
            'realized_to_planned':{},
            'planned_to_realized':{}
        }

    def add_action(self,on:Event_Change_Type,owner:str,action:Callable[[],None])->None:
        if on not in self._actions: raise KeyError("Unknown type of action in TreeEventConnector.")
        if owner in self._actions[on]: raise KeyError(f"An action was already added under the owner {owner}.")
        self._actions[on][owner] = action

    def _new_tree_item_events(self,tree:treemod.TreeItem|None)->None:
        if tree is None: return
        tree.add_action(self.label, 'add_child', self._new_event)

    def _new_event(self,item:treemod.TreeItem)->None:
        if self.date_label not in item.attributes: 
            return
        date = item.attributes[self.date_label]._value
        event = pf.Event(date)
        self.event_manager.add(event)
        item.add_data("event", event)
        item.add_action(self.label, 'on_removal', self._dismiss_event)
        item.attributes[self.date_label].add_action_on_edit(self.label, partial(self._move_event,item))
        event.add_action(
            'confirmed',
            self.label, 
            partial(self.editor.run_actions,'edit',item)
        )

    def _dismiss_event(self, item:treemod.TreeItem)->None:
        event:pf.Event = item.data["event"]
        self.event_manager.forget(event)

    def _move_event(self,item:treemod.TreeItem)->None:
        old_event:pf.Event = item.data["event"]
        new_event = pf.Event(date=item._attributes[self.date_label]._value)
        if old_event.planned:
            new_event.consider_as_planned()

        self.__do_if_moved_between_future_and_past(old_event, new_event)

        self.event_manager.forget(old_event)
        self.event_manager.add(new_event)
        item.data["event"] = new_event

    def __do_if_moved_between_future_and_past(self,old_event:pf.Event, new_event:pf.Event)->None:
        if old_event.realized and new_event.planned:
            for action in self._actions['realized_to_planned'].values(): action()

        elif old_event.planned and not old_event.confirmation_required and new_event.confirmation_required:
            for action in self._actions['planned_to_realized'].values(): action()