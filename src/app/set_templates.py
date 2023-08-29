from PIL import Image, ImageTk
from collections import OrderedDict

import src.core.tree as treemod
from decimal import Decimal
import src.lang.lang as lang

import src.core.currency as cur



from src.core.dates import default_date


def main(vocabulary:lang.Vocabulary, app_template:treemod.AppTemplate):

    cur.set_localization(app_template.locale_code)
    tvoc = vocabulary.subvocabulary("Templates")
    SCENARIO = tvoc("Scenario")
    INCOME = tvoc("Income")
    EXPENSE = tvoc("Expense")
    ITEM = tvoc("Item")
    DEBT = tvoc("Debt")
    NONFINANCIAL_DEBT = tvoc("Non_Monetary_Debt")

    INCOMES = tvoc("incomes")
    EXPENSES = tvoc("expenses")
    CURRENCY = tvoc("currency")
    AMOUNT = tvoc("amount")
    NAME =  tvoc("name")
    DATE = tvoc("date")
    DESCRIPTION = tvoc("description")

    income_icon = ImageTk.PhotoImage(Image.open("src/_icons/income.png"))
    expense_icon = ImageTk.PhotoImage(Image.open("src/_icons/expense.png"))
    item_icon = ImageTk.PhotoImage(Image.open("src/_icons/item.png"))
    debt_icon = ImageTk.PhotoImage(Image.open("src/_icons/debt.png"))
    nonmon_debt_icon = ImageTk.PhotoImage(Image.open("src/_icons/nonmonetary_debt.png"))

    locale_code = app_template.locale_code


    def extract_money_amount(assumed_money:str)->float:
        x = cur.convert_to_currency(assumed_money)
        if isinstance(x,tuple) and len(x)>0:
            return x[0]
        else:
            return 0

    def sum_incomes(item:treemod.TreeItem)->str:
        s = Decimal(0.0)
        for child in item._children:
            if child.tag==INCOME:
                s += child.attributes[AMOUNT].value
            elif child.tag==ITEM:
                s += Decimal(extract_money_amount(child.dependent_attributes[INCOMES].value))
        return "+"+ cur.CURRY_FORMATS[item.its_tree.attributes[CURRENCY].value].present(s,locale_code)
    
    def sum_expenses(item:treemod.TreeItem)->str:
        s = Decimal(0.0)
        for child in item._children:
            if child.tag==EXPENSE:
                s += child.attributes[AMOUNT].value
            elif child.tag==ITEM:
                s += Decimal(extract_money_amount(child.dependent_attributes[EXPENSES].value))
        return "-"+ cur.CURRY_FORMATS[item.its_tree.attributes[CURRENCY].value].present(s,locale_code)
    
    def print_hello_world(item:treemod.TreeItem)->None:
        print("Hello, world!!!")

    def default_amount_by_tree(item:treemod.TreeItem)->str:
        return "1" + cur.CURRY_FORMATS[item.its_tree.attributes[CURRENCY].value].symbol


    app_template.add(
        treemod.NewTemplate(
            SCENARIO,
            OrderedDict({
                NAME:SCENARIO,
                CURRENCY:({code:code for code in cur.CURRY_CODES}, cur.DEFAULT_CURRENCY_CODE),
                INCOMES: sum_incomes,
                EXPENSES: sum_expenses
            }),
            children=(INCOME, EXPENSE, ITEM, DEBT, NONFINANCIAL_DEBT)
        ),
        treemod.NewTemplate(
            INCOME,
            OrderedDict({NAME:INCOME, AMOUNT: "1 Kč", DATE: default_date(app_template.locale_code)}),
            children=(),
            icon_file=income_icon,
            variable_defaults={AMOUNT: default_amount_by_tree}
        ),
        treemod.NewTemplate(
            EXPENSE,
            OrderedDict({NAME:EXPENSE,AMOUNT: "1 Kč", DATE: default_date(app_template.locale_code)}),
            children=(),
            icon_file=expense_icon,
            variable_defaults={AMOUNT: default_amount_by_tree}
        ),
        treemod.NewTemplate(
            ITEM,
            OrderedDict({
                NAME:ITEM,
                INCOMES: sum_incomes,
                EXPENSES: sum_expenses
            }),
            children=(INCOME,EXPENSE,ITEM),
            user_def_cmds=OrderedDict({"Hello, world": print_hello_world}),
            icon_file=item_icon),

        treemod.NewTemplate(
            DEBT,
            OrderedDict({
                NAME:DEBT,
                AMOUNT:"1 Kč", 
                DATE: default_date(app_template.locale_code)
            }),
            children=(),
            icon_file=debt_icon,
            variable_defaults={AMOUNT: default_amount_by_tree}
        ),
        treemod.NewTemplate(
            NONFINANCIAL_DEBT,
            OrderedDict({
                NAME:NONFINANCIAL_DEBT,
                DESCRIPTION:"...", 
                DATE: default_date(app_template.locale_code)
            }),
            children=(),
            icon_file=nonmon_debt_icon
        ),
    )

