
import tkinter as tk
from src.tkgui.editor import Editor_Tk, Lang_Object
from src.core.editor import blank_case_template, new_editor
case_template = blank_case_template()
case_template.configure(currency_code="CZK")
lang = Lang_Object.get_lang_object("./test_hofi_localization/cs_cz.xml")


amount = case_template.attr.money(0)
case_template.add("Item", {"amount":amount, }, child_template_labels=("Item",),)
case_template.add_case_child_label("Item")
case_template.add_merging_rule("Item", {"amount":"sum"})
case_template.set_insertable("Item")

editor = new_editor(case_template, "cs_cz", lang=lang, ignore_duplicit_names=True)
win = tk.Tk()
editor_ui = Editor_Tk(editor, win, ({"amount":("amount",)}), lang = lang,)
editor_ui.configure(precision=2, trailing_zeros=True, use_thousands_separator=True)
case_A = editor.new_case("Case A")
parent = editor.new(case_A, "Item", "Parent")
item_I = editor.new(parent, "Item", "Item I")
item_II = editor.new(parent, "Item", "Item II")
item_I.set("amount", 5)
item_II.set("amount", 7)

win.mainloop()