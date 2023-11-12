import tkinter as tk
from src.tkgui.editor import Editor_Tk, Lang_Object
from src.core.editor import blank_case_template, new_editor, freeatt_child, freeatt_parent
from decimal import Decimal

case_template = blank_case_template()
case_template.configure(currency_code="CZK")
lang = Lang_Object.get_lang_object("./test_hofi_localization/cs_cz.xml")

amount = case_template.attr.money(1, custom_condition=lambda x: x>=0)
signed_amount = case_template.attr.money(enforce_sign=True)
rel_amount_attr = case_template.attr.quantity(unit="%", exponents={})
transaction_date = case_template.attr.date()

def total_amount_func(individual, totals)->Decimal:
    return sum(individual) + sum(totals)

def rel_amount(amount, total_amount)->Decimal:
    if total_amount==0: return 0
    else: return Decimal(100*amount)/Decimal(abs(total_amount))

total_amount = case_template.dependency(
    "total_amount", 
    lambda x,y: x+y,
    "total_income",
    "total_expense"
)
total_income = case_template.dependency(
    "total_income",
    total_amount_func,
    freeatt_child("income_amount",amount),
    freeatt_child("total_income",signed_amount)
)
total_expense = case_template.dependency(
    "total_expense",
    lambda x,y: -total_amount_func(x,y),
    freeatt_child("expense_amount",amount),
    freeatt_child("total_expense",signed_amount)
)


relative_income_amount = case_template.dependency(
    "relative_amount", 
    rel_amount,
    "income_amount",
    freeatt_parent("total_income", signed_amount)
)
relative_expense_amount = case_template.dependency(
    "relative_amount", 
    rel_amount,
    "expense_amount",
    freeatt_parent("total_expense", signed_amount)
)
relative_total_amount = case_template.dependency(
    "relative_amount", 
    rel_amount,
    "total_amount",
    freeatt_parent("total_amount", signed_amount)
)

case_template.add(
    "Income", 
    {"income_amount":amount, "relative_amount":rel_amount_attr, "date":transaction_date},
    dependencies=[relative_income_amount]
)
case_template.add(
    "Expense", 
    {"expense_amount":amount, "relative_amount":rel_amount_attr, "date":transaction_date},
    dependencies=[relative_expense_amount]
)
case_template.add(
    "Item", 
    {
        "total_amount":signed_amount, 
        "total_income":signed_amount,
        "total_expense":signed_amount,
        "relative_amount":rel_amount_attr
    }, 
    ("Income","Expense","Item"), 
    dependencies=[total_income, total_expense, total_amount, relative_total_amount]
)
case_template.add_case_child_label("Item")

case_template.set_case_template(
    {
        "total_amount":signed_amount, 
        "total_income":signed_amount,
        "total_expense":signed_amount
    }, 
    ("Income","Expense","Item"), 
    dependencies=[total_income, total_expense, total_amount]
)


editor = new_editor(case_template, "cs_cz", lang=lang)

win = tk.Tk()
editor_ui = Editor_Tk(
    editor, 
    win, 
    ({
        "amount":("income_amount","expense_amount","total_amount"),
        "relative_amount":("relative_amount",),
        "date":("date",)
    }),
    lang = lang,
    icons = {
        "Income":"src/tkgui/icons/income.png", 
        "Expense":"src/tkgui/icons/expense.png"
    }
)

editor_ui.configure(precision=2, trailing_zeros=True)

win.mainloop()
