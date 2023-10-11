import tkinter as tk
from src.ui.editor_elems import Item_Window
from src.core.editor import attr_entry_data
from src.core.attributes import attribute_factory
from src.cmd.commands import Controller


fac = attribute_factory(Controller())
intattr = fac.new('integer', 5, name="x")
realattr = fac.new('real', 15.1, name="y")


root = tk.Tk()
attrs = {
    'x':attr_entry_data(intattr),
    'y':attr_entry_data(realattr),
}


item_win = Item_Window(root, attrs)
item_win.ok()

root.mainloop()