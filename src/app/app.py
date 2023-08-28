import tkinter as tk
import src.controls.tree_editor as te
import src.controls.treemanager as tmg
import src.controls.treelist as tl
import src.core.tree as treemod
import src.reports.properties as pp
import src.lang.lang as lang
import os



root = tk.Tk()
root.geometry("800x600")


import src.app.set_templates
src.app.set_templates.main()


vocabulary = lang.Vocabulary()
vocabulary.load_xml(os.path.dirname(os.path.abspath(__file__))+'/loc', 'cs_cz')


left_frame = tk.Frame(root)
left_frame.pack(expand=1,fill=tk.BOTH,side=tk.LEFT)
manager_frame = tk.LabelFrame(left_frame, text=vocabulary("Manager_Title"))
manager_frame.pack(expand=1,fill=tk.BOTH)
properties_frame = tk.Frame(left_frame)
properties_frame.pack(expand=2,fill=tk.BOTH, side=tk.BOTTOM)
editor_frame = tk.LabelFrame(root, text=vocabulary("Edit_Frame_Label"))
editor_frame.pack(expand=1,fill=tk.BOTH,side=tk.RIGHT)


# create app parts and place their widgets into their respective places in the GUI
treelist = tl.TreeList(label='TreeList')

manager = tmg.Tree_Manager(
    treelist, 
    tree_tag="Scenario", 
    ui_master=manager_frame, 
    language_code='cs_cz'
)

editor = te.TreeEditor(
    editor_frame,
    label='TreeEditor', 
    displayed_attributes={vocabulary("Amount_Title"):("amount",)}, 
    language_code='cs_cz'
)

properties = pp.Properties(properties_frame,title=vocabulary("Properties"))


def clear_properties(*args): properties.clear()
# connect (initially independent) Editor and Manager
def add_tree_to_editor(tree:treemod.Tree): editor.load_tree(tree)
def remove_tree_from_editor(tree:treemod.Tree): editor.remove_tree(str(id(tree)))
manager.add_action_on_selection(add_tree_to_editor)
manager.add_action_on_deselection(remove_tree_from_editor)
editor.add_action(properties.label,'selection',properties.display)
editor.add_action(properties.label,'deselection',clear_properties)
editor.add_action(properties.label,'edit',properties.display)
editor.add_action(manager.label,'any_modification',manager.label_items_tree_as_modified)
editor.add_action(manager.label,'tree_removal',clear_properties)


import tkinter.messagebox as tkmsg
def discard_unsaved_changes():
    if manager.unsaved_trees:
        if tkmsg.askokcancel(
            vocabulary("Discard_Changes","Title"), 
            vocabulary("Discard_Changes","Content")):
            
            root.destroy()
    else:
        root.destroy()


root.protocol("WM_DELETE_WINDOW", discard_unsaved_changes)

if __name__=="__main__":
    root.mainloop()