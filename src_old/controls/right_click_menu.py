from typing import Callable, Dict
import tkinter as tk
from functools import partial


class RCMenu(tk.Menu):

    def add_single_command(
        self,
        label:str,
        cmd:Callable[[],None]
        )->None:

        super().add_command(label=label,command=self._add_cmd(cmd))

    def add_commands(self,labeled_commands:Dict[str,Callable[[],None]])->None:
        for label, command in labeled_commands.items():
            super().add_command(label=label,command=self._add_cmd(command))

    def _add_cmd(self,cmd:Callable)->Callable:
        def menu_cmd(*args,**kwargs): 
            cmd(*args,**kwargs)
            self.destroy()
        return partial(menu_cmd)