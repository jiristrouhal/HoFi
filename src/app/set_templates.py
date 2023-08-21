from PIL import Image, ImageTk
from collections import OrderedDict

import src.core.tree as treemod



def main():
    income_icon = ImageTk.PhotoImage(Image.open("src/_icons/income.png"))
    expense_icon = ImageTk.PhotoImage(Image.open("src/_icons/expense.png"))
    item_icon = ImageTk.PhotoImage(Image.open("src/_icons/item.png"))



    treemod.tt.attrs.Date_Attr.date_formatter.set("%d.%m.%Y")


    def item_relative_income(item:treemod.TreeItem)->str:
        return str(int(float(sum_incomes(item))/float(sum_incomes(item.parent))*100)) +' %'

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
            OrderedDict({
                "name":"New item",
                "total income": sum_incomes,
                "relative income": item_relative_income
            }),
            children=("Income","Expense","Item"),
            user_def_cmds=OrderedDict({"Hello, world":print_hello_world}),
            icon_file=item_icon),
    )