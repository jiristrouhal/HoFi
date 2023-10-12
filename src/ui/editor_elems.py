from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import tkcalendar as tkc
import abc


from typing import Dict, Optional, Any

from src.core.editor import Attr_Entry_Data
from src.core.editor import AttributeType



class Attribute_Entry(abc.ABC):

    def __init__(self, entry_data:Attr_Entry_Data, master:tk.Frame)->None:
        self.__data = entry_data
        self.__master = master
        self.__options:Dict[str,Any] = dict()
        self._create_entry()
        self._create_options()

    @property
    def data(self)->Attr_Entry_Data: return self.__data
    @property
    def master(self)->tk.Frame: return self.__master
    @abc.abstractproperty
    def widget(self)->tk.Widget: pass

    @abc.abstractmethod
    def _create_entry(self)->None: pass
    @abc.abstractmethod
    def _create_options(self)->None: pass
    @abc.abstractmethod
    def set(self,value:Any,value_label:str="")->None: pass

    def add_option(self,name:str,option:Any)->Any: self.__options[name] = option
    def option(self,name:str)->Any: return self.__options[name]
    @abc.abstractmethod
    def value(self, value_label:str="")->Any: pass


class Bool_Entry(Attribute_Entry):

    @property
    def widget(self)->tk.Checkbutton: return self.__value

    def _create_entry(self)->None: 
        self.__var = tk.BooleanVar(self.master, value=self.data.orig_value)
        self.__value = tk.Checkbutton(self.master, variable=self.__var, onvalue=True, offvalue=False)
    
    def _create_options(self) -> None: pass

    def set(self,value:bool,value_label:str="")->None: self.__var.set(value)

    def value(self, value_label: str = "") -> Any:
        return self.__var.get()
    

class Choice_Entry(Attribute_Entry):

    @property
    def widget(self) -> ttk.Combobox: return self.__choice

    def _create_entry(self) -> None:
        vcmd = (self.master.register(lambda x: x in self.data.values),'%P')
        self.__choice = ttk.Combobox(self.master, validate="key", validatecommand=vcmd)
        self.__choice.config(values=self.data.values)
        self.__choice.set(self.data.orig_value)

    def _create_options(self) -> None: pass

    def set(self, value:str, value_label:str="")->None:
        self.__choice.set(value)

    def value(self,value_label:str="")->Any:
        return self.__choice.get()


import datetime
class Date_Entry(Attribute_Entry):

    @property
    def widget(self)->tkc.DateEntry: return self.__date_entry

    def _create_entry(self) -> None:
        self.__date_entry = tkc.DateEntry(self.master, locale=self.data.locale_code)
        self.__date_entry.set_date(self.data.orig_value)
        
    def _create_options(self) -> None:
        pass

    def set(self, value:datetime.date, value_label:str="")->None:
        self.__date_entry.set_date(value)
    
    def value(self,value_label:str="")->datetime.date:
        return self.__date_entry.get_date()

    
class Money_Entry(Attribute_Entry):
    @property
    def widget(self)->tk.Widget: return self.__frame

    def _create_entry(self) -> None:
        self.__frame = tk.Frame(self.master)
        def validation_func(value:str)->bool: 
            return value=="" or self.data.validation_func(value)
        vcmd = (self.__frame.register(validation_func),'%P')
        self.__entry = tk.Entry(self.__frame, validate='key', validatecommand=vcmd, name="entry")
        self.__entry.insert(0,str(self.data.orig_value))
        self.__entry.grid(column=0,row=0)
    
    def _create_options(self) -> None: pass

    def set(self, value: Any, value_label: str = "") -> None:
        self.__entry.delete(0,tk.END)
        self.__entry.insert(0,value)

    def value(self, value_label: str = "") -> Any:
        return self.__entry.get()

class Quantity_Entry(Attribute_Entry):

    @property
    def widget(self)->tk.Frame: return self.__frame

    def _create_entry(self) -> None:
        def validation_func(value:str)->bool: 
            return (value=="" or self.data.validation_func(value))

        self.__frame = tk.Frame(self.master)
        vcmd = (self.__frame.register(validation_func),'%P')
        self.__value = tk.Entry(self.__frame, validate='key', validatecommand=vcmd)
        self.__value.insert(0, self.data.orig_value)
        self.__value.grid(row=0, column=0)
    
    def _create_options(self) -> None:
        def validate_unit(unit:str)->bool:  return unit in self.data.options['unit'].keys()
        unit_vcmd = (self.__frame.register(validate_unit),'%P')
        self.add_option('unit', ttk.Combobox(
            self.__frame, 
            width=7,
            values=list(self.data.options['unit'].keys()), 
            name="unit",
            validate="key",
            validatecommand=unit_vcmd,
        ))
        self.option('unit').set(self.data.chosen_options['unit'])
        self.option('unit').grid(row=0,column=1)

    def set(self,value:Any,value_label:str=""): 
        if value_label=="":
            self.__value.delete(0,tk.END)
            self.__value.insert(0,value)
        elif value_label=="unit":
            self.option("unit").set(value)
    
    def value(self, value_label:str = "") -> Any:
        if value_label=="": return self.__value.get()
        elif value_label=="unit": return self.option("unit").get()


class Number_Entry(Attribute_Entry):

    @property
    def widget(self)->tk.Widget: return self.__value
        
    def _create_entry(self) -> None:
        def validation_func(value:str)->bool: 
            return value=="" or self.data.validation_func(value)
        vcmd = (self.master.register(validation_func),'%P')
        self.__value = tk.Entry(self.master, validate='key', validatecommand=vcmd)
        self.__value.insert(0,str(self.data.orig_value))

    def _create_options(self) -> None: pass

    def set(self, value:Any, value_label:str="")->None:
        self.__value.delete(0, tk.END)
        self.__value.insert(0, value)

    def value(self, value_label: str = "")->str:
        return self.__value.get()


class Text_Entry(Attribute_Entry):

    @property
    def widget(self)->tk.Text: return self.__text
    
    def _create_entry(self)->None:
        self.__text = tk.Text(self.master)
        self.__text.insert(1.0, self.data.orig_value)
    
    def _create_options(self) -> None: pass
    
    def set(self,value:str,value_label:str="")->None: 
        self.__text.delete(1.0, tk.END)
        self.__text.insert(1.0, value)

    def value(self, value_label: str = "") -> Any:
        return self.__text.get(1.0, tk.END)


        

class Entry_Creator: 

    def new(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Attribute_Entry: 
        match entry_data.type:
            case 'bool': return self.__boolean(entry_data,master)
            case 'choice': return self.__choice(entry_data,master)
            case 'date': return self.__date(entry_data,master)
            case 'integer': return self.__number(entry_data,master)
            case 'money': return self.__money(entry_data,master)
            case 'real': return self.__number(entry_data,master)
            case 'quantity': return self.__quantity(entry_data,master)
            case 'text': return self.__text(entry_data,master)
            case _: 
                raise Entry_Creator.UnknownEntryType(entry_data.type)

    def __boolean(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Attribute_Entry:
        return Bool_Entry(entry_data, master)
    
    def __choice(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Choice_Entry:
        return Choice_Entry(entry_data, master)
    
    def __date(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Date_Entry:
        return Date_Entry(entry_data, master)
    
    def __money(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Money_Entry:
        return Money_Entry(entry_data, master)
    
    def __number(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Number_Entry:
        return Number_Entry(entry_data, master)

    def __quantity(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Quantity_Entry:
        return Quantity_Entry(entry_data, master)
    
    def __text(self, entry_data:Attr_Entry_Data, master:tk.Frame)->Text_Entry:
        return Text_Entry(entry_data, master)
    

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
        attr_name.grid(column=0, row=row, sticky=tk.E)
        entry.widget.grid(column=1, row=row, sticky=tk.W)

    def __create_button_frame(self)->None:
        bf = tk.Frame(self.__win, name="button_frame")
        tk.Button(bf, text="Revert", command=lambda: None, name="revert").grid(row=0,column=0)
        tk.Button(bf, text="OK", command=lambda: None).grid(row=0,column=1)
        tk.Button(bf, text="Cancel", command=lambda: None).grid(row=0,column=2)
        bf.grid(row=1)
        