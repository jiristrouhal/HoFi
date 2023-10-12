import tkinter as tk
from src.ui.editor_elems import Item_Window
from src.core.attributes import attribute_factory
from src.cmd.commands import Controller


fac = attribute_factory(Controller(), "cs_cz")

boolattr = fac.new('bool',True)
intattr = fac.new('integer', 5, name="x")
realattr = fac.new('real', 15.1, name="y")
length = fac.newqu(4.5, 'length', 'm', exponents={'k':3})
choice = fac.new('choice', 'A', 'The Choice', options=['A','B'])
date = fac.new('date')


root = tk.Tk()
attrs = {
    'flag':boolattr,
    'x':intattr,
    'y':realattr,
    'length':length,
    'choice':choice,
    'date':date
}


item_win = Item_Window(root, attrs)
item_win.ok()

root.mainloop()