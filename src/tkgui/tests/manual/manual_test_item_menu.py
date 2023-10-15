import tkinter as tk
from src.tkgui.item_actions import Item_Menu_Tk
from src.core.attributes import attribute_factory
from src.cmd.commands import Controller
from decimal import Decimal


fac = attribute_factory(Controller(), "cs_cz")

boolattr = fac.new('bool',True)
intattr = fac.new('integer', 5, name="x")
positive_intattr = fac.new('integer', 5, name="x+", custom_condition=lambda x: x>0)
realattr = fac.new('real', 15.1, name="y")
length = fac.newqu(4.5, 'length', 'm', exponents={'k':3}, custom_condition=lambda x: x>0)
temperature = fac.newqu(20, 'length', '°C', exponents={}, custom_condition=lambda x: Decimal(str(x))>=Decimal('-273.15'))
temperature.add_unit(
    symbol="K",
    exponents={'m':-3},
    from_basic=lambda x: Decimal(str(x))+Decimal('273.15'),
    to_basic=lambda x: Decimal(str(x))-Decimal('273.15')
)
choice = fac.new('choice', 'A', 'The Choice', options=['A','B'])
date = fac.new('date')
cost = fac.new('money', 58.12)


intattr_dependent = fac.new('integer', 5, name="2*x")
intattr_dependent.add_dependency(lambda x: Decimal(2)*x, intattr)


root = tk.Tk()
attrs = {
    'enable':boolattr,
    'x':intattr,
    'f(x)':intattr_dependent,
    'x+':positive_intattr,
    'y':realattr,
    'length':length,
    'temperature':temperature,
    'choice':choice,
    'date':date,
    'cost':cost
}
from src.core.item import ItemImpl, ItemCreator

item = ItemImpl("The Item", attrs, ItemCreator())



item_menu = Item_Menu_Tk(root)
item_menu.open({"action 1":lambda: None})

root.bind()

root.mainloop()