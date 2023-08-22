from PIL import Image, ImageTk
from collections import OrderedDict

import src.core.tree as treemod



def main():
    income_icon = ImageTk.PhotoImage(Image.open("src/_icons/income.png"))
    expense_icon = ImageTk.PhotoImage(Image.open("src/_icons/expense.png"))
    item_icon = ImageTk.PhotoImage(Image.open("src/_icons/item.png"))
    debt_icon = ImageTk.PhotoImage(Image.open("src/_icons/debt.png"))

    treemod.tt.attrs.Date_Attr.date_formatter.set("%d.%m.%Y")


    def sum_incomes(item:treemod.TreeItem)->int:
        s = 0
        for child in item._children:
            if child.tag=="Income":
                s += child.attributes["amount"].value
            elif child.tag=="Item":
                s += child.dependent_attributes["total income"].value
        return s
    
    def sum_expenses(item:treemod.TreeItem)->int:
        s = 0
        for child in item._children:
            if child.tag=="Expense":
                s += child.attributes["amount"].value
            elif child.tag=="Item":
                s += child.dependent_attributes["total expense"].value
        return s

    def print_hello_world(item:treemod.TreeItem)->None:
        print("Hello, world!!!")

    treemod.tt.clear()
    treemod.tt.add(
        treemod.tt.NewTemplate('Scenario',{"name":"Scenario","total income": sum_incomes, "total expense": sum_expenses},children=("Income","Expense","Item","Debt")),
        treemod.tt.NewTemplate('Income',{"name":"Income","amount":1, "date":"1.1.2023"},children=(),icon_file=income_icon),
        treemod.tt.NewTemplate('Expense',{"name":"Expense","amount":1, "date":"1.1.2023"},children=(),icon_file=expense_icon),
        treemod.tt.NewTemplate(
            'Item',
            OrderedDict({
                "name":"Item",
                "total income": sum_incomes,
                "total expense": sum_expenses,
            }),
            children=("Income","Expense","Item"),
            user_def_cmds=OrderedDict({"Hello, world":print_hello_world}),
            icon_file=item_icon),

        treemod.tt.NewTemplate('Debt',{"name":"Debt","amount":1, "date":"1.1.2023"},children=(),icon_file=debt_icon),
    )

