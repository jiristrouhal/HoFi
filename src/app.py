import tkinter as tk
import controls.tree_editor as te
import controls.treemanager as tmg
import controls.treelist as tl
import core.tree as treemod
import reports.properties as pp


EDIT_FRAME_LABEL = "Editor"
MANAGER_TITLE = "Manager"


root = tk.Tk()
root.geometry("800x600")


from PIL import Image, ImageTk


income_icon = ImageTk.PhotoImage(Image.open("src/icons/income.png"))
expense_icon = ImageTk.PhotoImage(Image.open("src/icons/expense.png"))
item_icon = ImageTk.PhotoImage(Image.open("src/icons/item.png"))


edit_frame = tk.LabelFrame(root, text=EDIT_FRAME_LABEL)
manager_frame = tk.LabelFrame(root, text=MANAGER_TITLE)
properties_frame = tk.Frame(root,width=50,height=50)


manager_frame.pack(expand=1,fill=tk.BOTH)
edit_frame.pack(expand=2,fill=tk.BOTH)
properties_frame.pack(expand=1,fill=tk.BOTH)


treemod.tt.attrs.Date_Attr.date_formatter.set("%d.%m.%Y")

treemod.tt.clear()
treemod.tt.add(
    treemod.tt.NewTemplate('Scenario',{"name":"New"},children=("Income","Expense","Item")),
    treemod.tt.NewTemplate('Income',{"name":"New","amount":1, "date":"1.1.2023"},children=(),icon_file=income_icon),
    treemod.tt.NewTemplate('Expense',{"name":"New","amount":1},children=(),icon_file=expense_icon),
    treemod.tt.NewTemplate('Item',{"name":"New"},children=("Income","Expense","Item"),icon_file=item_icon),
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