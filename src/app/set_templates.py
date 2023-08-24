from PIL import Image, ImageTk
from collections import OrderedDict

import src.core.tree as treemod



def main():
    income_icon = ImageTk.PhotoImage(Image.open("src/_icons/income.png"))
    expense_icon = ImageTk.PhotoImage(Image.open("src/_icons/expense.png"))
    item_icon = ImageTk.PhotoImage(Image.open("src/_icons/item.png"))
    debt_icon = ImageTk.PhotoImage(Image.open("src/_icons/debt.png"))
    nonmon_debt_icon = ImageTk.PhotoImage(Image.open("src/_icons/nonmonetary_debt.png"))

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

    def default_amount_by_tree(item:treemod.TreeItem)->str:
        return "12" + treemod.CURRY_FORMATS[item.get_its_tree().attributes["currency"].value].symbol

    treemod.tt.clear()
    treemod.tt.add(
        treemod.tt.NewTemplate(
            'Scenario',
            {
                "name":"Scenario",
                "currency":({"USD":"USD", 'CZK':'CZK', 'EUR':'EUR'},'USD')
            },
            children=("Income","Expense","Item","Debt",'Non_monetary_debt')
        ),
        treemod.tt.NewTemplate(
            'Income',
            {"name":"Income","amount": "1 Kč", "date":"1.1.2023"},
            children=(),
            icon_file=income_icon,
            variable_defaults={"amount": default_amount_by_tree}
        ),
        treemod.tt.NewTemplate(
            'Expense',
            {"name":"Expense","amount": "1 Kč", "date":"1.1.2023"},
            children=(),
            icon_file=expense_icon,
            variable_defaults={"amount": default_amount_by_tree}
        ),
        treemod.tt.NewTemplate(
            'Item',
            OrderedDict({
                "name":"Item"
            }),
            children=("Income","Expense","Item"),
            user_def_cmds=OrderedDict({"Hello, world":print_hello_world}),
            icon_file=item_icon),

        treemod.tt.NewTemplate(
            'Debt',
            {
                "name":"Debt",
                "amount":"1 Kč", 
                "date":"1.1.2023"
            },
            children=(),
            icon_file=debt_icon,
            variable_defaults={"amount": default_amount_by_tree}
        ),
        treemod.tt.NewTemplate(
            'Non_monetary_debt',
            {
                "name":"Non-monetary debt",
                "description":"...", 
                "date":"1.1.2023"
            },
            children=(),
            icon_file=nonmon_debt_icon
        ),
    )

