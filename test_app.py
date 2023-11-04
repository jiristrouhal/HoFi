import tkinter as tk
from src.tkgui.editor import Editor_Tk
from src.core.editor import blank_case_template, new_editor, freeatt, freeatt_parent, freeatt_child


case_template = blank_case_template()
attr = case_template.attr


hmotnost = attr.quantity(unit="kg",exponents={"k":3, "m":-3},custom_condition=lambda x: x>=0, init_value=1.0)
podil_hm = attr.real(init_value=1.0, custom_condition=lambda x: x>=0)


dep_podil_hm = case_template.dependency(
    "podíl_hm.", 
    lambda m,mtot: m/mtot,
    freeatt('hmotnost'), 
    freeatt_parent('hmotnost', hmotnost)
)
hm_suma = case_template.dependency(
    'hmotnost', 
    lambda mi: sum(mi), 
    freeatt_child('hmotnost', hmotnost)
)


case_template.add(
    'Díl', 
    {'hmotnost':hmotnost, "podíl_hm.":podil_hm}, 
    (),
    dependencies=[dep_podil_hm]
)
case_template.add(
    'Sestava', 
    {'hmotnost':hmotnost, "podíl_hm.":podil_hm}, 
    ('Sestava','Díl'), 
    dependencies=[hm_suma, dep_podil_hm]
)
case_template.add_case_child_label('Sestava','Díl')
editor = new_editor(case_template, "en_us")


win = tk.Tk()


ui = Editor_Tk(editor, win, ('hmotnost',"podíl_hm."))


win.mainloop()