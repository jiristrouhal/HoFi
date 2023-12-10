import tkinter as tk
from src.tkgui.editor import Editor_Tk, Lang_Object
from src.core.editor import blank_case_template, new_editor, freeatt_child
from decimal import Decimal

case_template = blank_case_template()
case_template.configure(currency_code="CZK")
lang = Lang_Object.get_lang_object("./test_hofi_localization/cs_cz.xml")


amount = case_template.attr.money(0, custom_condition=lambda x: x>=0)


def total_amount_func(individual)->Decimal:
    return sum(individual)


total_income = case_template.dependency(
    "total_income",
    total_amount_func,
    freeatt_child("income_amount",amount),
)

case_template.add("Income", {"income_amount":amount, })
case_template.add_merging_rule("Income", {"income_amount":"sum"})
case_template.set_case_template(
    {
        "total_income":amount
    }, 
    child_template_labels=("Income", ), 
    dependencies=[total_income]
)
editor = new_editor(case_template, "cs_cz", lang=lang, ignore_duplicit_names=True)

win = tk.Tk()
editor_ui = Editor_Tk(
    editor, 
    win, 
    ({
        "income_amount":("income_amount",)
    }),
    lang = lang,
)

editor_ui.configure(precision=2, trailing_zeros=True, use_thousands_separator=True)
