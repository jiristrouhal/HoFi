import tkinter as tk
from src.tkgui.editor import Editor_Tk
from src.core.editor import blank_case_template, new_editor, freeatt_child, Lang_Object


case_template = blank_case_template()
attr = case_template.attr

hmotnost = attr.quantity(
    unit="kg",
    exponents={"k":3, "m":-3}, 
    custom_condition=lambda x: x>=0, 
    init_value=0.0
)
suma_hm = case_template.dependency('hmotnost', lambda x: sum(x), freeatt_child('hmotnost',hmotnost))

case_template.add('part', {'hmotnost':hmotnost}, ())
case_template.add(
    'assembly', 
    {'hmotnost':hmotnost},  
    ('part', 'assembly'),
    dependencies = [suma_hm]
)

case_template.add_case_child_label('part', 'assembly')
editor = new_editor(case_template, "cs_cz")
lang = Lang_Object.get_lang_object("localization/cs_cz.xml")

win = tk.Tk()
ui = Editor_Tk(editor, win, {'hmotnost':('hmotnost',)}, lang=lang)

win.mainloop()