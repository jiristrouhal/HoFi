import tkinter as tk
import tree_editor as te
import treemanager as tmg
import treelist as tl
import tree as treemod
import properties as pp


EDIT_FRAME_LABEL = "Editor"
MANAGER_TITLE = "Manager"


root = tk.Tk()
root.geometry("800x600")


edit_frame = tk.LabelFrame(root, text=EDIT_FRAME_LABEL)
manager_frame = tk.LabelFrame(root, text=MANAGER_TITLE)
properties_frame = tk.Frame(root,width=50,height=50)


manager_frame.pack(expand=1,fill=tk.BOTH)
edit_frame.pack(expand=2,fill=tk.BOTH)
properties_frame.pack(expand=1,fill=tk.BOTH)


treemod.tt.attrs.Date_Attr.date_formatter.set("%d.%m.%Y")

treemod.tt.clear()
treemod.tt.add(
    treemod.tt.NewTemplate('Scenario',{"name":"New"},children=("Income","Expense","Item"),icon_file="./src/icons/black_square.png"),
    treemod.tt.NewTemplate('Income',{"name":"New","amount":1, "date":"1.1.2023"},children=()),
    treemod.tt.NewTemplate('Expense',{"name":"New","amount":1},children=()),
    treemod.tt.NewTemplate('Item',{"name":"New"},children=("Income","Expense","Item")),
)


treelist = tl.TreeList(label='TreeList')
manager = tmg.Tree_Manager(treelist, tree_tag="Scenario", ui_master=manager_frame)
editor = te.TreeEditor(edit_frame,label='TreeEditor')
properties = pp.Properties(properties_frame)


def add_tree_to_editor(tree:treemod.Tree):
    editor.load_tree(tree)
def remove_tree_from_editor(tree:treemod.Tree):
    editor.remove_tree(str(id(tree)))


manager.add_action_on_selection(add_tree_to_editor)
manager.add_action_on_deselection(remove_tree_from_editor)

editor.add_action_on_selection(properties.display)
editor.add_action_on_unselection(properties.clear)
editor.add_action_on_edit(properties.redraw)
editor.add_action_on_tree_removal(properties.clear)



if __name__=="__main__":
    root.mainloop()