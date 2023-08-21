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


income_icon = ImageTk.PhotoImage(Image.open("src/_icons/income.png"))
expense_icon = ImageTk.PhotoImage(Image.open("src/_icons/expense.png"))
item_icon = ImageTk.PhotoImage(Image.open("src/_icons/item.png"))



manager_frame = tk.LabelFrame(root, text=MANAGER_TITLE)
manager_frame.pack(expand=1,fill=tk.BOTH)
bottom_frame = tk.Frame(root)
bottom_frame.pack(expand=1,fill=tk.BOTH,side=tk.BOTTOM)

editor_frame = tk.LabelFrame(bottom_frame, text=EDIT_FRAME_LABEL)
properties_frame = tk.Frame(bottom_frame)

editor_frame.pack(expand=1,fill=tk.BOTH,side=tk.LEFT)
properties_frame.pack(expand=1,fill=tk.BOTH, side=tk.RIGHT)


treemod.tt.attrs.Date_Attr.date_formatter.set("%d.%m.%Y")


def item_relative_income(item:treemod.TreeItem)->str:
    return str(int(float(sum_incomes(item))/sum_incomes(item.parent)*100)) +' %'

def sum_incomes(item:treemod.TreeItem)->int:
    s = 0
    for child in item._children:
        if child.tag=="Income":
            s += child.attributes["amount"].value
        elif child.tag=="Item":
            s += child.dependent_attributes["total income"].value
    return s

def print_hello_world(item:treemod.TreeItem)->None:
    print("Hello, world!!!")

treemod.tt.clear()
treemod.tt.add(
    treemod.tt.NewTemplate('Scenario',{"name":"New","total income": sum_incomes},children=("Income","Expense","Item")),
    treemod.tt.NewTemplate('Income',{"name":"New income","amount":1, "date":"1.1.2023"},children=(),icon_file=income_icon),
    treemod.tt.NewTemplate('Expense',{"name":"New expense","amount":1, "date":"1.1.2023"},children=(),icon_file=expense_icon),
    treemod.tt.NewTemplate(
        'Item',
        {
            "name":"New item",
            "total income": sum_incomes,
            "relative income": item_relative_income
        },
        children=("Income","Expense","Item"),
        user_def_cmds={"Hello, world":print_hello_world},
        icon_file=item_icon),
)


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