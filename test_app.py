import tkinter as tk
from src.tkgui.editor import Editor_Tk
from src.core.editor import blank_case_template, new_editor


case_template = blank_case_template()
attr = case_template.attr
case_template.add(
    'Díl', 
    {
        'hmotnost':attr.quantity(
            unit="kg",
            exponents={"k":3},
            custom_condition=lambda x: x>0, 
            init_value=1.0
        ),
        "podíl_hm.":attr.real(1, custom_condition=lambda x: x>0)
    }, 
    (),
    dependencies=[
        case_template.dependency("podíl_hm.", lambda m,mtot: m/mtot, 'hmotnost', '<hmotnost:quantity>'),
    ]
)
case_template.add(
    'Sestava', 
    {
        'hmotnost':attr.quantity(
            unit="kg",
            exponents={"k":3},
            custom_condition=lambda x: x>0, 
            init_value=1.0
        ),
        "podíl_hm.":attr.real(1, custom_condition=lambda x: x>0)
    }, 
    ('Sestava','Díl'), 
    dependencies=[
        case_template.dependency('hmotnost', lambda mi: sum(mi), '[hmotnost:quantity]'),
        case_template.dependency("podíl_hm.", lambda m,mtot: m/mtot, 'hmotnost', '<hmotnost:quantity>'),
    ]
)
case_template.add_case_child_label('Sestava','Díl')
editor = new_editor(case_template, "en_us")


win = tk.Tk()


ui = Editor_Tk(editor, win, ('hmotnost',"podíl_hm."))


win.mainloop()