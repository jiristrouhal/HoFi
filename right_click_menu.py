from typing import Callable
import tkinter as tk
import tkinter.ttk as ttk
from functools import partial


def add_treeview_item_cmd(
    menu:tk.Menu,
    label:str,
    cmd:Callable[[],None]
    )->None:

    if menu.index(label)==None:
        menu.add_command(label=label,command=_add_cmd(cmd,menu))


def _add_cmd(cmd:Callable,menu:tk.Menu)->Callable:
    def menu_cmd(menu:tk.Menu,*args,**kwargs): 
        cmd(*args,**kwargs)
        menu.destroy()
    return partial(menu_cmd,menu)