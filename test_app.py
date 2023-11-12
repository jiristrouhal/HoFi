import tkinter as tk
from src.tkgui.editor import Editor_Tk
from src.core.editor import blank_case_template, new_editor, freeatt_child, Lang_Object



lang = Lang_Object.get_lang_object("test_app_localization/cs_cz.xml")
case_template = blank_case_template()
attr = case_template.attr


mass = attr.quantity(
    unit="kg",
    exponents={"k":3, "m":-3}, 
    custom_condition=lambda x: x>=0, 
    init_value=0.0
)
sum_of_masses = case_template.dependency('mass', lambda x: sum(x), freeatt_child('mass',mass))

case_template.add('part', {'mass':mass}, ())
case_template.add(
    'assembly', 
    {'mass':mass},  
    ('part', 'assembly'),
    dependencies = [sum_of_masses]
)

case_template.add_case_child_label('part', 'assembly')
editor = new_editor(case_template, "cs_cz", lang=lang)


win = tk.Tk()
ui = Editor_Tk(editor, win, {'mass':('mass',)}, lang=lang)

win.mainloop()