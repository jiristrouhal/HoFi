from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import tkcalendar as tkc
import abc
from typing import Dict, Optional, Any


class Attribute_Entry(abc.ABC):

    def __init__(self, attr:Attribute, master:tk.Frame)->None:
        self.__attr = attr
        self.__master = master
        self.__options:Dict[str,Any] = dict()
        self._create_entry()

    @property
    def attr(self)->Attribute: return self.__attr
    @property
    def master(self)->tk.Frame: return self.__master
    @abc.abstractproperty
    def value(self)->Any: pass
    @abc.abstractproperty
    def widget(self)->tk.Widget: pass

    @abc.abstractmethod
    def _create_entry(self)->None: pass

    def ok(self)->None:
        self.attr.set(self._confirmed_value())

    @abc.abstractmethod
    def _confirmed_value(self)->Any: pass
    @abc.abstractmethod
    def revert(self)->None: pass
    @abc.abstractmethod
    def set(self,value:Any)->None: pass

    def add_option(self,name:str,option:Any)->Any: self.__options[name] = option
    def option(self,name:str)->Any: return self.__options[name]


class Bool_Entry(Attribute_Entry):

    @property
    def value(self) -> Any: return self.__var.get()
    @property
    def widget(self)->tk.Checkbutton: return self.__value

    def _create_entry(self)->None: 
        self.__var = tk.BooleanVar(self.master, value=self.attr.value)
        self.__value = tk.Checkbutton(self.master, variable=self.__var, onvalue=True, offvalue=False)
    
    def _confirmed_value(self)->bool:
        return self.__var.get()

    def revert(self)->None:
        self.set(self.attr.value)

    def set(self,value:bool)->None: self.__var.set(value)
    

from src.core.attributes import Choice_Attribute
class Choice_Entry(Attribute_Entry):

    @property
    def value(self)->Any: return self.__choice.get()
    @property
    def widget(self) -> ttk.Combobox: return self.__choice

    def _create_entry(self) -> None:
        assert(isinstance(self.attr,Choice_Attribute))
        ops = self.attr.options
        vcmd = (self.master.register(lambda x: x in ops),'%P')
        self.__choice = ttk.Combobox(self.master, validate="key", validatecommand=vcmd)
        self.__choice.config(values=ops)
        self.__choice.set(self.attr.value)

    def _confirmed_value(self)->str:
        return self.__choice.get()

    def revert(self)->None:
        self.__choice.set(self.attr.value)

    def set(self, value:str)->None:
        self.__choice.set(value)


import datetime
class Date_Entry(Attribute_Entry):

    @property
    def value(self)->datetime.date: return self.__date_entry.get_date()
    @property
    def widget(self)->tkc.DateEntry: return self.__date_entry

    def _create_entry(self) -> None:
        self.__date_entry = tkc.DateEntry(self.master, locale=self.attr.factory.locale_code)
        self.__date_entry.set_date(self.attr.value)
        
    def _confirmed_value(self)->datetime.date:
        return self.__date_entry.get_date()
    
    def revert(self)->None:
        self.__date_entry.set_date(self.attr.value)

    def set(self, value:datetime.date)->None:
        self.__date_entry.set_date(value)


from src.core.attributes import Number_Attribute
class Number_Entry(Attribute_Entry):

    @property
    def value(self)->str:  return self._value.get()
    @property
    def widget(self)->tk.Widget: return self._value
        
    def _create_entry(self) -> None:
        vcmd = (self.master.register((self._text_is_valid_value)),'%P')
        self._value = tk.Entry(self.master, validate='key', validatecommand=vcmd)
        self._value.insert(0, self.attr.print())

    def _confirmed_value(self)->float|Decimal:
        str_value = self._value.get()
        if str_value in ("","+","-"): return self.attr.value
        else: return Decimal(str_value.replace(",","."))
  
    def revert(self)->None:
        self._value.delete(0,tk.END)
        self._value.insert(0, self.attr.print())

    def set(self, value:Any)->None:
        old_value = self.value
        self._value.delete(0, tk.END)
        self._value.insert(0, value)
        if value != "" and self.value=="":
            self._value.insert(0, str(old_value))
 
    def _text_is_valid_value(self,text:str)->bool:
        assert(isinstance(self.attr, Number_Attribute))
        text = text.replace(",",".")

        if text in ("","-","+"): return True

        elif self.attr._is_text_a_number(text):
            return self.attr.is_valid(Decimal(text))
        else:
            return False

    

from src.core.attributes import Monetary_Attribute
class Money_Entry(Number_Entry):
    @property
    def widget(self)->tk.Widget: return self.__frame

    def _create_entry(self) -> None:
        self.__frame = tk.Frame(self.master)
        vcmd = (self.__frame.register(self._text_is_valid_value),'%P')
        self._value = tk.Entry(self.__frame, validate='key', validatecommand=vcmd)
        assert(isinstance(self.attr, Monetary_Attribute))
        self._value.insert(0, str(self.attr.print(show_symbol=False)))
        currency = Monetary_Attribute.Currencies[self.attr.factory.currency_code]
        symbol = tk.Label(self.__frame,text=currency.symbol)
        if currency.symbol_before_value and self.attr.prefer_symbol_before_value():
            symbol.grid(column=0,row=0)
            self._value.grid(column=1,row=0)
        else:
            self._value.grid(column=0,row=0)
            symbol.grid(column=1,row=0)

    def revert(self)->None:
        self._value.delete(0,tk.END)
        assert(isinstance(self.attr, Monetary_Attribute))
        entry_init_value = self.attr.print(show_symbol=False, trailing_zeros=False)
        self._value.insert(0,entry_init_value)


from src.core.attributes import Quantity
from decimal import Decimal
class Quantity_Entry(Number_Entry):

    @property
    def unit(self)->str: return self.__unit.get()
    @property
    def value(self) -> str: return self._value.get()
    @property
    def widget(self)->tk.Frame: return self.__frame

    def _create_entry(self) -> None: 
        self.__frame = tk.Frame(self.master)

        assert(isinstance(self.attr,Quantity))
        scaled_units = self.attr.scaled_units_single_str
        def validate_unit(unit:str)->bool:  
            return unit in scaled_units
        unit_vcmd = (self.__frame.register(validate_unit),'%P')
        self.__prev_scaled_unit = self.attr.prefix + self.attr.unit
        self.__unit_var = tk.StringVar(self.__frame)
        self.__unit = ttk.Combobox(
            self.__frame, 
            width=7,
            values=scaled_units, 
            name="unit",
            validate="key",
            validatecommand=unit_vcmd,
            textvariable=self.__unit_var
        )
        self.__unit.set(self.attr.prefix+self.attr.unit)
        self.__unit.grid(row=0,column=1)
        self.__unit_var.trace_add("write", self.__update_displayed_value_on_unit_update)

        vcmd = (self.__frame.register(self._text_is_valid_quantity_value),'%P')
        self._value = tk.Entry(self.__frame, validate='key', validatecommand=vcmd)
        self._value.grid(row=0, column=0)
        self.__update_value(self.attr.value)


    def __update_value(self,new_value:Any)->None:
        str_value = str(new_value)
        assert(isinstance(self.attr,Quantity))
        if self.attr.comma_as_dec_separator: str_value = str_value.replace(".",",")
        self._value.delete(0, tk.END)
        self._value.insert(0, str_value)

    def __update_displayed_value_on_unit_update(self, *args)->None:
        assert(isinstance(self.attr,Quantity))
        if self.value in ("","+","-"): 
            source_value = self.attr.value
            source_unit = self.attr.default_scaled_unit
        else:
            source_value = Decimal(self.value.replace(",","."))
            source_unit = self.__prev_scaled_unit
        target_unit = self.__unit.get()
        target_value = str(self.attr.convert(source_value, source_unit, target_unit))
        if "." in target_value: target_value = target_value.rstrip("0").rstrip(".")
        self.__update_value(target_value)
        self.__prev_scaled_unit = self.__unit.get()

    def _text_is_valid_quantity_value(self,text:str)->bool:
        assert(isinstance(self.attr, Quantity))
        if text in ("","-","+"): return True

        text = text.replace(",",".")
        if self.attr._is_text_a_number(text):   
            source_unit, target_unit = self.__unit.get(), self.attr.default_scaled_unit
            adjusted_value = self.attr.convert(
                Decimal(text),
                source_unit,
                target_unit
            )
            return self.attr.is_valid(adjusted_value)
        else:
            return False

    def _confirmed_value(self)->Decimal:
        assert(isinstance(self.attr,Quantity))
        scaled_unit = self.__unit.get()
        self.attr.set_scaled_unit(scaled_unit)
        value = self._value.get().replace(",",".")

        if value in ("","+","-"): 
            return self.attr.value
        else:
            return self.attr.convert(
                Decimal(value),
                scaled_unit,
                self.attr.default_scaled_unit
            )
        
    def set(self,value:Any)->None:
        if self._text_is_valid_quantity_value(str(value)):
            super().set(value)

    def revert(self)->None:
        assert(isinstance(self.attr,Quantity))
        self.__unit.set(self.attr.prefix+self.attr.unit)
        self.__update_value(self.attr.print(include_unit=False))
    
    def set_unit(self, value:str)->None:
        self.__unit.set(value)
        self.__update_displayed_value_on_unit_update()
        

class Text_Entry(Attribute_Entry):

    @property
    def widget(self)->tk.Text: return self.__text
    @property
    def value(self) -> Any: return self.__text.get(1.0, tk.END)
    
    def _create_entry(self)->None:
        self.__text = tk.Text(self.master)
        self.__text.insert(1.0, self.attr.value)

    def _confirmed_value(self)->str:
        return self.__text.get(1.0, tk.END)[:-1]

    def revert(self)->None:
        self.__text.delete(1.0, tk.END)
        self.__text.insert(1.0, self.attr.value)
    
    def set(self,value:str)->None: 
        self.__text.delete(1.0, tk.END)
        self.__text.insert(1.0, value)

        
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


from typing import List
from src.core.editor import Item_Menu, Item_Window
class Item_Window_Tk(Item_Window):
    
    def __init__(self, root:Optional[tk.Tk])->None:
        super().__init__()
        self.__win = tk.Toplevel(root)
        self.__ecr = Entry_Creator()

    @property
    def entries(self)->List[Attribute_Entry]: 
        return self.__entries.copy()

    def _build_window(self, attributes: Dict[str, Attribute]):
        self.__create_entries(attributes)
        self.__create_button_frame()

    def _destroy_window(self):
        self.__win.destroy()
        self.__entries.clear()

    def ok(self)->None: 
        okbutton:tk.Button = self.__win.nametowidget('button_frame').nametowidget('ok')
        okbutton.invoke()

    def __ok(self)->None:
        confirmed_vals:Dict[Attribute,Any] = dict()
        for entry in self.__entries: 
            confirmed_vals[entry.attr] = entry._confirmed_value()

        Attribute.set_multiple({entry.attr:confirmed_vals[entry.attr] for entry in self.__entries})
        self.__win.destroy()

    def __revert(self)->None:
        for entry in self.__entries: entry.revert()

    def __cancel(self)->None:
        self.__win.destroy()
        
    def __create_entries(self,attrs:Dict[str,Attribute])->None:
        """Create entries for attributes without assigned dependencies."""
        frame = tk.Frame(self.__win, name="entries")
        row = 0
        self.__entries:List[Attribute_Entry] = list()
        for label,attr in attrs.items():
            if not attr.dependent:
                self.__add_attr(label,attr,row,frame)
                row += 1
        frame.grid(row=0)
            
    def __add_attr(self,label:str,attr:Attribute,row:int,frame:tk.Frame)->None:
        attr_name = tk.Label(frame, text=label)
        entry = self.__ecr.new(attr, frame)
        attr_name.grid(column=0, row=row, sticky=tk.E)
        entry.widget.grid(column=1, row=row, sticky=tk.W)
        self.__entries.append(entry)

    def __create_button_frame(self)->None:
        bf = tk.Frame(self.__win, name="button_frame")
        tk.Button(bf, text="Revert", command=lambda: self.__revert(), name="revert").grid(row=0,column=0)
        tk.Button(bf, text="OK", command=lambda: self.__ok(),  name="ok").grid(row=0,column=1)
        tk.Button(bf, text="Cancel", command=lambda: self.__cancel()).grid(row=0,column=2)
        bf.grid(row=1)
        

class Item_Menu_Tk(Item_Menu):

    def _build_menu(self) -> None:
        pass
    def _destroy_menu(self) -> None:
        pass