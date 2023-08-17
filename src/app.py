import tkinter as tk
import tree_editor as te
import treemanager as tmg
import treelist as tl
import tree as treemod
import properties as pp


EDIT_FRAME_LABEL = "Editor"


root = tk.Tk()
root.geometry("800x600")


edit_frame = tk.LabelFrame(root, text=EDIT_FRAME_LABEL)
manager_frame = tk.Frame(root)
properties_frame = tk.Frame(root,width=50,height=50)

manager_frame.pack(expand=1,fill=tk.BOTH)
edit_frame.pack(expand=2,fill=tk.BOTH)
properties_frame.pack(expand=1,fill=tk.BOTH)

treelist = tl.TreeList(label='TreeList')
manager = tmg.Tree_Manager(treelist, manager_frame)
editor = te.TreeEditor(edit_frame,label='TreeEditor')
properties = pp.Properties(properties_frame)


def add_tree_to_editor(tree:treemod.Tree):
    editor.load_tree(tree)
def remove_tree_from_editor(tree:treemod.Tree):
    editor.remove_tree(str(id(tree)))


manager.add_action_on_selection(add_tree_to_editor)
manager.add_action_on_deselection(remove_tree_from_editor)
editor.add_action_on_selection(properties.display)
editor.add_action_on_deselection(properties.clear)
editor.add_action_on_edit(properties.redraw)



if __name__=="__main__":
    root.mainloop()