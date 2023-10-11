from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import tkcalendar as tkc


from typing import Dict, Optional

from src.core.editor import Attr_Entry_Data
from src.core.editor import AttributeType


class Entry_Creator: 

    def new(self, entry_data:Attr_Entry_Data, master:tk.Frame)->tk.Widget: 
        match entry_data.type:
            case 'bool': return self.__boolean(entry_data,master)
            case 'choice': return self.__choice(entry_data,master)
            case 'date': return self.__date(entry_data,master)
            case 'integer': return self.__number(entry_data,master)
            case 'money': return self.__money(entry_data,master)
            case 'real': return self.__number(entry_data,master)
            case 'text': return self.__text(entry_data,master)
            case _: 
                raise Entry_Creator.UnknownEntryType(entry_data.type)

    def __boolean(self, entry_data:Attr_Entry_Data, master:tk.Frame)->tk.Checkbutton:
        widget = tk.Checkbutton(master)
        return widget
    
    def __choice(self, entry_data:Attr_Entry_Data, master:tk.Frame)->ttk.Combobox:
        widget = ttk.Combobox(master)
        return widget
    
    def __date(self, entry_data:Attr_Entry_Data, master:tk.Frame)->tkc.Calendar:
        widget = tkc.Calendar(master)
        return widget
    
    def __money(self, entry_data:Attr_Entry_Data, master:tk.Frame)->tk.Frame:
        def validation_func(value:str)->bool: 
            return value=="" or entry_data.validation_func(value)

        vcmd = (master.register(validation_func),'%P')
        frame = tk.Frame(master)
        entry = tk.Entry(frame, validate='key', validatecommand=vcmd, name="entry")
        entry.insert(0,str(entry_data.orig_value))
        entry.grid(column=0,row=0)
        return frame
    
    def __number(self, entry_data:Attr_Entry_Data, master:tk.Frame)->tk.Entry:
        def validation_func(value:str)->bool: 
            return value=="" or entry_data.validation_func(value)

        vcmd = (master.register(validation_func),'%P')
        widget = tk.Entry(master, validate='key', validatecommand=vcmd)
        widget.insert(0,str(entry_data.orig_value))
        return widget
    
    def __text(self, entry_data:Attr_Entry_Data, master:tk.Frame)->tk.Text:
        widget = tk.Text(master)
        return widget
    

    class UnknownEntryType(Exception): pass


class Item_Window:
    
    def __init__(self, root:Optional[tk.Tk], entry_data:Dict[str,Attr_Entry_Data]={})->None:
        self.__win = tk.Toplevel(root)
        self.__ecr = Entry_Creator()
        self.__create_entries(entry_data)
        self.__create_button_frame()

    def ok(self)->None: 
        okbutton:tk.Button = self.__win.nametowidget('button_frame').nametowidget('revert')
        okbutton.invoke()
        
    def __create_entries(self,entry_data:Dict[str,Attr_Entry_Data])->None:
        frame = tk.Frame(self.__win, name="entries")
        row = 0
        for label,attr in entry_data.items():
            self.__add_attr(label,attr,row,frame)
            row += 1
        frame.grid(row=0)
            
    def __add_attr(self,label:str,attr:Attr_Entry_Data,row:int,frame:tk.Frame)->None:
        attr_name = tk.Label(frame, text=label)
        entry = self.__ecr.new(attr, frame)
        attr_name.grid(column=0, row=row)
        entry.grid(column=1, row=row)

    def __create_button_frame(self)->None:
        bf = tk.Frame(self.__win, name="button_frame")
        tk.Button(bf, text="Revert", command=lambda: None, name="revert").grid(row=0,column=0)
        tk.Button(bf, text="OK", command=lambda: None).grid(row=0,column=1)
        tk.Button(bf, text="Cancel", command=lambda: None).grid(row=0,column=2)
        bf.grid(row=1)
        