import tkinter as tk
from src.tkgui.editor import Editor_Tk
from src.core.editor import blank_case_template, new_editor, freeatt_child


case_template = blank_case_template()
attr = case_template.attr

hmotnost = attr.quantity(
    unit="kg",
    exponents={"k":3, "m":-3}, 
    custom_condition=lambda x: x>=0, 
    init_value=0.0
)
suma_hm = case_template.dependency('hmotnost', lambda x: sum(x), freeatt_child('hmotnost',hmotnost))

case_template.add('Díl', {'hmotnost':hmotnost}, ())
case_template.add(
    'Sestava', 
    {'hmotnost':hmotnost},  
    ('Díl', 'Sestava'),
    dependencies = [suma_hm]
)

case_template.add_case_child_label('Díl', 'Sestava')
editor = new_editor(case_template, "en_us")
win = tk.Tk()
ui = Editor_Tk(editor, win, ('hmotnost',))

win.mainloop()