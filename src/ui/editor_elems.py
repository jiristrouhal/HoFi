from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import tkcalendar as tkc
import abc
from typing import Dict, Optional, Any

from src.core.editor import AttributeType


class Attribute_Entry(abc.ABC):

    def __init__(self, attr:Attribute, master:tk.Frame)->None:
        self.__attr = attr
        self.__master = master
        self.__options:Dict[str,Any] = dict()
        self._create_entry()
        self._create_options()

    @property
    def attr(self)->Attribute: return self.__attr
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
        self.__var = tk.BooleanVar(self.master, value=self.attr.value)
        self.__value = tk.Checkbutton(self.master, variable=self.__var, onvalue=True, offvalue=False)
    
    def _create_options(self) -> None: pass

    def set(self,value:bool,value_label:str="")->None: self.__var.set(value)

    def value(self, value_label: str = "") -> Any:
        return self.__var.get()
    

from src.core.attributes import Choice_Attribute
class Choice_Entry(Attribute_Entry):

    @property
    def widget(self) -> ttk.Combobox: return self.__choice

    def _create_entry(self) -> None:
        assert(isinstance(self.attr,Choice_Attribute))
        ops = self.attr.options
        vcmd = (self.master.register(lambda x: x in ops),'%P')
        self.__choice = ttk.Combobox(self.master, validate="key", validatecommand=vcmd)
        self.__choice.config(values=ops)
        self.__choice.set(self.attr.value)

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
        self.__date_entry = tkc.DateEntry(self.master, locale=self.attr.factory.locale_code)
        self.__date_entry.set_date(self.attr.value)
        
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
            return value=="" or self.attr._is_text_valid(value)
        vcmd = (self.__frame.register(validation_func),'%P')
        self.__entry = tk.Entry(self.__frame, validate='key', validatecommand=vcmd, name="entry")
        self.__entry.insert(0,str(self.attr.value))
        self.__entry.grid(column=0,row=0)
    
    def _create_options(self) -> None: pass

    def set(self, value: Any, value_label: str = "") -> None:
        self.__entry.delete(0,tk.END)
        self.__entry.insert(0,value)

    def value(self, value_label: str = "") -> Any:
        return self.__entry.get()


from src.core.attributes import Quantity
class Quantity_Entry(Attribute_Entry):

    @property
    def widget(self)->tk.Frame: return self.__frame

    def _create_entry(self) -> None:
        def validation_func(value:str)->bool: 
            return (value=="" or self.attr._is_text_valid(value))

        self.__frame = tk.Frame(self.master)
        vcmd = (self.__frame.register(validation_func),'%P')
        self.__value = tk.Entry(self.__frame, validate='key', validatecommand=vcmd)
        self.__value.grid(row=0, column=0)
        self.__update_value(self.attr.value)
    
    def _create_options(self) -> None:
        assert(isinstance(self.attr,Quantity))
        scaled_units = self.attr.scaled_units_single_str
        def validate_unit(unit:str)->bool:  
            return unit in scaled_units
        unit_vcmd = (self.__frame.register(validate_unit),'%P')
        self.add_option('unit', ttk.Combobox(
            self.__frame, 
            width=7,
            values=scaled_units, 
            name="unit",
            validate="key",
            validatecommand=unit_vcmd,
        ))
        self.option('unit').set(self.attr.prefix+self.attr.unit)
        self.option('unit').grid(row=0,column=1)

    def __update_value(self,new_value:Any)->None:
        self.__value.delete(0, tk.END)
        self.__value.insert(0, self.attr.value)

    def set(self,value:Any,value_label:str=""):
        assert(isinstance(self.attr,Quantity))
        if value_label=="":
            self.__update_value(value)
        elif value_label=="unit":
            self.option("unit").set(value)
            self.__update_value(self.attr.print(include_unit=False))
    
    def value(self, value_label:str = "") -> Any:
        if value_label=="": return self.__value.get()
        elif value_label=="unit": return self.option("unit").get()


class Number_Entry(Attribute_Entry):

    @property
    def widget(self)->tk.Widget: return self.__value
        
    def _create_entry(self) -> None:
        def validation_func(value:str)->bool: 
            return value=="" or self.attr._is_text_valid(value)
        vcmd = (self.master.register(validation_func),'%P')
        self.__value = tk.Entry(self.master, validate='key', validatecommand=vcmd)
        self.__value.insert(0,str(self.attr.print()))

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
        self.__text.insert(1.0, self.attr.value)
    
    def _create_options(self) -> None: pass
    
    def set(self,value:str,value_label:str="")->None: 
        self.__text.delete(1.0, tk.END)
        self.__text.insert(1.0, value)

    def value(self, value_label: str = "") -> Any:
        return self.__text.get(1.0, tk.END)


        
from src.core.attributes import Attribute
class Entry_Creator: 

    def new(self, attr:Attribute, master:tk.Frame)->Attribute_Entry: 
        match attr.type:
            case 'bool': return self.__boolean(attr,master)
            case 'choice': return self.__choice(attr,master)
            case 'date': return self.__date(attr,master)
            case 'integer': return self.__number(attr,master)
            case 'money': return self.__money(attr,master)
            case 'real': return self.__number(attr,master)
            case 'quantity': return self.__quantity(attr,master)
            case 'text': return self.__text(attr,master)
            case _: 
                raise Entry_Creator.UnknownEntryType(attr.type)

    def __boolean(self, attr:Attribute, master:tk.Frame)->Attribute_Entry:
        return Bool_Entry(attr, master)
    
    def __choice(self, attr:Attribute, master:tk.Frame)->Choice_Entry:
        return Choice_Entry(attr, master)
    
    def __date(self, attr:Attribute, master:tk.Frame)->Date_Entry:
        return Date_Entry(attr, master)
    
    def __money(self, attr:Attribute, master:tk.Frame)->Money_Entry:
        return Money_Entry(attr, master)
    
    def __number(self, attr:Attribute, master:tk.Frame)->Number_Entry:
        return Number_Entry(attr, master)

    def __quantity(self, attr:Attribute, master:tk.Frame)->Quantity_Entry:
        return Quantity_Entry(attr, master)
    
    def __text(self, attr:Attribute, master:tk.Frame)->Text_Entry:
        return Text_Entry(attr, master)
    

    class UnknownEntryType(Exception): pass


class Item_Window:
    
    def __init__(self, root:Optional[tk.Tk], attrs:Dict[str,Attribute]={})->None:
        self.__win = tk.Toplevel(root)
        self.__ecr = Entry_Creator()
        self.__create_entries(attrs)
        self.__create_button_frame()

    def ok(self)->None: 
        okbutton:tk.Button = self.__win.nametowidget('button_frame').nametowidget('revert')
        okbutton.invoke()
        
    def __create_entries(self,attrs:Dict[str,Attribute])->None:
        frame = tk.Frame(self.__win, name="entries")
        row = 0
        for label,attr in attrs.items():
            self.__add_attr(label,attr,row,frame)
            row += 1
        frame.grid(row=0)
            
    def __add_attr(self,label:str,attr:Attribute,row:int,frame:tk.Frame)->None:
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
        