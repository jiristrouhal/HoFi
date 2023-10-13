import tkinter as tk
from src.ui.editor_elems import Item_Window
from src.core.attributes import attribute_factory
from src.cmd.commands import Controller
from decimal import Decimal


fac = attribute_factory(Controller(), "cs_cz")

boolattr = fac.new('bool',True)
intattr = fac.new('integer', 5, name="x")
realattr = fac.new('real', 15.1, name="y")
length = fac.newqu(4.5, 'length', 'm', exponents={'k':3})
temperature = fac.newqu(20, 'length', '°C', exponents={})
temperature.add_unit(
    symbol="K",
    exponents={'m':-3},
    from_basic=lambda x: Decimal(str(x))+Decimal('273.15'),
    to_basic=lambda x: Decimal(str(x))-Decimal('273.15')
)
choice = fac.new('choice', 'A', 'The Choice', options=['A','B'])
date = fac.new('date')
cost = fac.new('money', 58.12)


root = tk.Tk()
attrs = {
    'flag':boolattr,
    'x':intattr,
    'y':realattr,
    'length':length,
    'temperature':temperature,
    'choice':choice,
    'date':date,
    'cost':cost
}


item_win = Item_Window(root, attrs)
item_win.ok()

root.mainloop()