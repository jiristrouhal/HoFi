import tkinter as tk
import tkinter.messagebox as tkmsg
import os
from typing import List, Tuple, Literal


import src.controls.tree_editor as te
import src.controls.treemanager as tmg
import src.controls.treelist as tl
import src.core.tree as treemod
import src.reports.properties as pp
import src.lang.lang as lang
import src.core.tree_templates as temp
import src.app.set_templates
import src.app.tree_event_connector as tec
import src.events.past_and_future as pf

import dataclasses

@dataclasses.dataclass
class Display_Properties:
    properties_window:pp.Properties
    item:treemod.TreeItem = dataclasses.field(init=False)
    def run(self,item:treemod.TreeItem):
        self.item = item
        self.properties_window.display(self.item)
    def undo(self)->None:
        self.properties_window.clear()
    def redo(self)->None:
        self.properties_window.display(self.item)


@dataclasses.dataclass
class Mark_Tree_As_Updated:
    manager:tmg.Tree_Manager
    item:treemod.TreeItem = dataclasses.field(init=False)
    previous_state:List|Tuple|Literal[''] = dataclasses.field(init=False)
    new_state:List|Tuple|Literal[''] = dataclasses.field(init=False)
    tree_id:str = dataclasses.field(init=False)
    modified_before:bool = dataclasses.field(init=False)
    def run(self,item:treemod.TreeItem):
        self.tree_id = item.its_tree.data["treemanager_id"]
        self.previous_state = self.manager._view.item(self.tree_id)["values"].copy()

        self.modified_before = item.its_tree in self.manager._treelist._modified_trees
        self.manager.label_items_tree_as_modified(item)

        self.new_state = self.manager._view.item(self.tree_id)["values"].copy()
        self.item = item

    def undo(self)->None:
        self.manager._view.item(self.tree_id,values=self.previous_state)
        if not self.modified_before: self.manager.label_tree_as_ok(self.item.its_tree)
    def redo(self)->None:
        self.manager.label_items_tree_as_modified(self.item)


@dataclasses.dataclass
class Clear_Properties:
    properties_window:pp.Properties
    item:treemod.TreeItem = dataclasses.field(init=False)
    def run(self,item:treemod.TreeItem):
        self.item = item
        self.properties_window.clear()
    def undo(self)->None:
        self.properties_window.display(self.item)
    def redo(self)->None:
        self.properties_window.clear()


def build_app(locale_code:lang.Locale_Code):

    root = tk.Tk()
    root.geometry("800x600")

    vocabulary = lang.Vocabulary()
    vocabulary.load_xml(os.path.dirname(os.path.abspath(__file__))+'/loc', locale_code)


    root_pane = tk.PanedWindow(root,orient=tk.HORIZONTAL)
    root_pane.pack(fill=tk.BOTH, expand=1)
    left_pane = tk.PanedWindow(root_pane, orient=tk.VERTICAL)
    root_pane.add(left_pane)
    manager_frame = tk.LabelFrame(left_pane, text=vocabulary("Manager_Title"))
    left_pane.add(manager_frame)
    properties_frame = tk.Frame(left_pane)
    left_pane.add(properties_frame)
    editor_frame = tk.LabelFrame(root, text=vocabulary("Edit_Frame_Label"))
    root_pane.add(editor_frame)


    app_template = temp.AppTemplate(locale_code,name_attr=vocabulary("Templates","name"))

    editor = te.TreeEditor(
        app_template,
        editor_frame,
        label='TreeEditor', 
        displayed_attributes={
            vocabulary("Amount_Title"):(vocabulary("Templates","amount"),),
            "Status":(vocabulary("Templates","status"),)
        },
        ignored_attributes=(vocabulary("Templates","last_status"),) 
    )
    editor.widget.column(vocabulary("Amount_Title"),anchor=tk.E,width=100)
    editor.widget.column("Status",anchor=tk.CENTER,width=100)
    
    event_manager = pf.Event_Manager()
    connector = tec.TreeEventConnector(
        editor, 
        event_manager, 
        date_label=vocabulary("Templates","date")
    )
    def notify_item_moved_from_future_to_past_or_present()->None:
        tkmsg.showinfo( 
            vocabulary("Item_Moved_from_Future_to_Past","Title"),
            vocabulary("Item_Moved_from_Future_to_Past","Content"),
        )
    def notify_that_realized_item_moved_to_future()->None:
        tkmsg.showinfo( 
            vocabulary("Realized_Item_Moved_to_Future","Title"),
            vocabulary("Realized_Item_Moved_to_Future","Content"),
        )

    connector.add_action('planned_to_realized','app', 
        notify_item_moved_from_future_to_past_or_present)
    connector.add_action('realized_to_planned','app', 
        notify_that_realized_item_moved_to_future)

    src.app.set_templates.main(vocabulary, app_template, event_manager)


    # create app parts and place their widgets into their respective places in the GUI
    treelist = tl.TreeList(label='TreeList')

    manager = tmg.Tree_Manager(
        treelist, 
        tree_tag=vocabulary("Templates", "Scenario"), 
        ui_master=manager_frame, 
        app_template=app_template
    )

    properties = pp.Properties(
        properties_frame,
        title=vocabulary("Properties"),
        name_attr=vocabulary("Templates","name"),
        ignored=(vocabulary("Templates","last_status"),)
    )

    def clear_properties(*args): properties.clear()
    # connect (initially independent) Editor and Manager
    def add_tree_to_editor(tree:treemod.Tree): 
        editor.load_tree(tree)
    def remove_tree_from_editor(tree:treemod.Tree): 
        editor.remove_tree(str(id(tree)))

    

    manager.add_action_on_selection(add_tree_to_editor)
    manager.add_action_on_deselection(remove_tree_from_editor)
    editor.add_action(properties.label,'selection',Display_Properties(properties))
    editor.add_action(properties.label,'deselection',Clear_Properties(properties))
    editor.add_action(properties.label,'edit',Display_Properties(properties))
    editor.add_action(manager.label,'any_modification',Mark_Tree_As_Updated(manager))
    editor.add_tree_manipulation_action(manager.label,'tree_removal',clear_properties)

    def discard_unsaved_changes():
        if manager.unsaved_trees:
            if tkmsg.askokcancel(
                vocabulary("Discard_Changes","Title"), 
                vocabulary("Discard_Changes","Content")):
                
                root.destroy()
        else:
            root.destroy()


    root.protocol("WM_DELETE_WINDOW", discard_unsaved_changes)
    return root


if __name__=="__main__":
    build_app('cs_cz').mainloop()