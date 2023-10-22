import tkinter as tk
from src.tkgui.editor import Editor_Tk
from src.core.editor import blank_case_template, new_editor


case_template = blank_case_template()
editor = new_editor(case_template, "en_us")


win = tk.Tk()


ui = Editor_Tk(editor, win)


win.mainloop()