import tkinter as tk
from te_tree.tkgui.editor import Editor_Tk, Lang_Object
from te_tree.core.editor import blank_case_template, new_editor, freeatt_child, freeatt_parent
from decimal import Decimal

case_template = blank_case_template()
case_template.configure(currency_code="CZK")
lang = Lang_Object.get_lang_object("./localization/cs_cz.xml")

amount = case_template.attr.money(0, custom_condition=lambda x: x>=0)
rel_amount_attr = case_template.attr.quantity(unit="%", exponents={})
transaction_date = case_template.attr.date()
comment = case_template.attr.text()

def total_amount_func(individual, totals)->Decimal:
    return sum(individual) + sum(totals)

def rel_amount(amount, total_amount)->Decimal:
    if total_amount==0: return 0
    else: return Decimal(100*abs(amount))/Decimal(abs(total_amount))

total_amount = case_template.dependency(
    "total_amount",
    lambda x,y: x-y,
    "total_income",
    "total_expense"
)
total_income = case_template.dependency(
    "total_income",
    total_amount_func,
    freeatt_child("income_amount",amount),
    freeatt_child("total_income",amount)
)
total_expense = case_template.dependency(
    "total_expense",
    lambda x,y: total_amount_func(x,y),
    freeatt_child("expense_amount",amount),
    freeatt_child("total_expense",amount)
)


relative_income_amount = case_template.dependency(
    "relative_income_amount",
    rel_amount,
    "income_amount",
    freeatt_parent("total_income", amount)
)
relative_expense_amount = case_template.dependency(
    "relative_expense_amount",
    rel_amount,
    "expense_amount",
    freeatt_parent("total_expense", amount)
)
relative_item_income_amount = case_template.dependency(
    "relative_income_amount",
    rel_amount,
    "total_income",
    freeatt_parent("total_income", amount)
)
relative_item_expense_amount = case_template.dependency(
    "relative_expense_amount",
    rel_amount,
    "total_expense",
    freeatt_parent("total_expense", amount)
)


debt_sum = case_template.dependency(
    "total_debt_amount",
    lambda x: sum(x),
    freeatt_child("debt_amount", amount)
)

case_template.add(
    "Debts",
    {
        "total_debt_amount":amount,
        "comment":comment
    },
    child_template_labels=("Debt","NonMonetary_Debt"),
    dependencies=[debt_sum]
)


case_template.add(
    "Debt",
    {
        "debt_amount":amount,
        "date":transaction_date,
        "comment":comment
    },
    child_template_labels=()
)

case_template.add(
    "NonMonetary_Debt",
    {
        "date":transaction_date,
        "comment":comment
    },
    child_template_labels=()
)


case_template.add(
    "Income",
    {
        "income_amount":amount,
        "relative_income_amount":rel_amount_attr,
        "date":transaction_date,
        "comment":comment
    },
    dependencies=[relative_income_amount]
)
case_template.add_merging_rule(
    "Income",
    {"income_amount":"sum", "relative_income_amount":"sum", "date":"max", "comment":"join_texts"}
)

case_template.add(
    "Expense",
    {
        "expense_amount":amount,
        "relative_expense_amount":rel_amount_attr,
        "date":transaction_date,
        "comment":comment
    },
    dependencies=[relative_expense_amount]
)
case_template.add_merging_rule(
    "Expense",
    {"expense_amount":"sum", "relative_expense_amount":"sum", "date":"max", "comment":"join_texts"}
)
case_template.add(
    "Item",
    {
        "total_amount":amount,
        "total_income":amount,
        "total_expense":amount,
        "relative_income_amount":rel_amount_attr,
        "relative_expense_amount":rel_amount_attr,
        "comment":comment
    },
    ("Income","Expense","Item"),
    dependencies=[total_income, total_expense, total_amount, relative_item_income_amount, relative_item_expense_amount]
)


case_template.set_case_template(
    {
        "total_amount":amount,
        "total_income":amount,
        "total_expense":amount
    },
    child_template_labels=("Debts","Income","Expense","Item"),
    dependencies=[total_income, total_expense, total_amount]
)


case_template.set_insertable("Item")
editor = new_editor(case_template, "cs_cz", lang=lang, ignore_duplicit_names=True)

win = tk.Tk()
editor_ui = Editor_Tk(
    editor,
    win,
    ({
        "income_amount":("income_amount","total_income"),
        "expense_amount":("expense_amount", "total_expense", "debt_amount","total_debt_amount"),
        "relative_income_amount":("relative_income_amount","relative_amount"),
        "relative_expense_amount":("relative_expense_amount","relative_amount"),
        "date":("date",)
    }),
    lang = lang,
    icons = {
        "Income":"src/tkgui/icons/income.png",
        "Expense":"src/tkgui/icons/expense.png",
        "Debts":"src/tkgui/icons/debt.png",
        "NonMonetary_Debt":"src/tkgui/icons/nonmonetary_debt.png",
    }
)

editor_ui.configure(precision=2, trailing_zeros=True, use_thousands_separator=True)


win.title("HoFi")


def main():
    win.mainloop()
