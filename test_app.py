import tkinter as tk
from src.tkgui.editor import Editor_Tk
from src.core.editor import blank_case_template, new_editor


case_template = blank_case_template()
attr = case_template.attr
case_template.add("Item_A", {'x':attr.integer(4)}, ('Item_B',))
case_template.add(
    "Item_B", 
    {'x':attr.integer(5), 'y':attr.integer(4)}, 
    ('Item_B',), 
    dependencies=[
        case_template.dependency('x', lambda x: sum(x), '[x:integer]'),
        case_template.dependency('y', lambda x: 1000*x, 'x')
    ]
)
case_template.add_case_child_label("Item_A", "Item_B")
editor = new_editor(case_template, "en_us")


win = tk.Tk()


ui = Editor_Tk(editor, win, ("x",'y'))


win.mainloop()