import sys
sys.path.insert(1, "src")


from typing import Tuple


from src.controls.tree_editor import TreeEditor
import src.app.past_and_future as pf
import src.core.tree as treemod


class TreeEventConnector:

    def __init__(
        self, 
        editor:TreeEditor, 
        event_manager:pf.Event_Manager, 
        date_labels:Tuple[str,...],
        )->None:

        event_manager_id = str(id(event_manager))
        editor.add_action(event_manager_id, 'load_tree', self._new_tree_item_events)
        self.label = str(id(self))
        self.date_labels = date_labels
        self.event_manager = event_manager


    def _new_tree_item_events(self,tree:treemod.Tree)->None:
        tree.add_action(self.label, 'add_child', self._new_event)

    def _new_event(self,item:treemod.TreeItem)->None:
        for label in self.date_labels:
            if label in item.attributes: 
                date = item.attributes[label]._value
                self.event_manager.add(pf.Event(date))
                
