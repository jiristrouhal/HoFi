import tkinter as tk


import src.controls.tree_editor as te
import src.controls.treemanager as tmg
import src.controls.treelist as tl
import src.core.tree as treemod
import src.reports.properties as pp


EDIT_FRAME_LABEL = "Editor"
MANAGER_TITLE = "Manager"


root = tk.Tk()
root.geometry("800x600")


import src.app.set_templates
src.app.set_templates.main()



manager_frame = tk.LabelFrame(root, text=MANAGER_TITLE)
manager_frame.pack(expand=1,fill=tk.BOTH)
bottom_frame = tk.Frame(root)
bottom_frame.pack(expand=1,fill=tk.BOTH,side=tk.BOTTOM)

editor_frame = tk.LabelFrame(bottom_frame, text=EDIT_FRAME_LABEL)
properties_frame = tk.Frame(bottom_frame)

editor_frame.pack(expand=1,fill=tk.BOTH,side=tk.LEFT)
properties_frame.pack(expand=1,fill=tk.BOTH, side=tk.RIGHT)



treelist = tl.TreeList(label='TreeList')
manager = tmg.Tree_Manager(treelist, tree_tag="Scenario", ui_master=manager_frame)
editor = te.TreeEditor(editor_frame,label='TreeEditor')
properties = pp.Properties(properties_frame)


def add_tree_to_editor(tree:treemod.Tree):
    editor.load_tree(tree)
def remove_tree_from_editor(tree:treemod.Tree):
    editor.remove_tree(str(id(tree)))


manager.add_action_on_selection(add_tree_to_editor)
manager.add_action_on_deselection(remove_tree_from_editor)

editor.add_action_on_selection(properties.display)
editor.add_action_on_unselection(properties.clear)
editor.add_action_on_edit(properties.display)
editor.add_action_on_tree_removal(properties.clear)



if __name__=="__main__":
    root.mainloop()