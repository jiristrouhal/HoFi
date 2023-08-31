import sys
sys.path.insert(1, "src")


from src.controls.tree_editor import TreeEditor
import src.app.past_and_future as pf
import src.core.tree as treemod


class TreeEventConnector:

    def __init__(
        self, 
        editor:TreeEditor, 
        event_manager:pf.Event_Manager, 
        date_label:str,
        )->None:

        event_manager_id = str(id(event_manager))
        editor.add_action(event_manager_id, 'load_tree', self._new_tree_item_events)
        self.label = str(id(self))
        self.date_label = date_label
        self.event_manager = event_manager


    def _new_tree_item_events(self,tree:treemod.Tree)->None:
        tree.add_action(self.label, 'add_child', self._new_event)

    def _new_event(self,item:treemod.TreeItem)->None:
        if self.date_label not in item.attributes: 
            return
        date = item.attributes[self.date_label]._value
        event = pf.Event(date)
        self.event_manager.add(event)
        item.add_data("event", event)
        item.add_action(self.label, 'on_removal', self._dismiss_event)

    def _dismiss_event(self, item:treemod.TreeItem)->None:
        event:pf.Event = item.data["event"]
        self.event_manager.forget(event)
