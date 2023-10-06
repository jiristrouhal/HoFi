from __future__ import annotations

import dataclasses
from typing import Dict, Any, Callable

from src.core.item import Item, Parentage_Data
from src.cmd.commands import Command, Empty_Command
from src.core.attributes import Attribute, Attribute_Factory, Attribute_List


@dataclasses.dataclass
class Timepoint_Data:
    tline:Timeline
    item:Item
    time:Any


@dataclasses.dataclass
class Add_Timepoint(Command):
    data:Timepoint_Data
    timepoint:Timepoint = dataclasses.field(init=False)
    def run(self)->None:
        if self.data.time not in self.data.tline.timepoints:
            self.timepoint = self.data.tline.create_timepoint(self.data.time)
            self.data.tline._add_timepoint(self.data.time, self.timepoint)
        else:
            self.timepoint = self.data.tline.timepoints[self.data.time]
        self.timepoint._add_item(self.data.item)

    def undo(self)->None:
        self.timepoint._remove_item(self.data.item)
        if not self.timepoint.has_items():
            self.data.tline._remove_timepoint(self.data.time)

    def redo(self)->None:
        if not self.timepoint.has_items():
            self.data.tline._add_timepoint(self.data.time, self.timepoint)
        self.timepoint._add_item(self.data.item)


@dataclasses.dataclass
class Remove_Timepoint(Command):
    data:Timepoint_Data
    timepoint:Timepoint = dataclasses.field(init=False)
    def run(self)->None:
        self.timepoint = self.data.tline.timepoints[self.data.time]
        self.timepoint._remove_item(self.data.item)
        if not self.timepoint.has_items():
            self.data.tline._remove_timepoint(self.data.time)

    def undo(self)->None:
        if not self.timepoint.has_items():
            self.data.tline._add_timepoint(self.data.time, self.timepoint)
            self.timepoint._add_item(self.data.item)

    def redo(self)->None:
        self.timepoint._remove_item(self.data.item)
        if not self.timepoint.has_items():
            self.data.tline._remove_timepoint(self.data.time)


from typing import Tuple, List
@dataclasses.dataclass(frozen=True)
class Binding:
    dependent:str
    func:Callable[[Any],Any]
    free:Tuple[str,...]


class Timeline:
    
    def __init__(
        self, 
        root:Item, 
        attribute_factory:Attribute_Factory,
        timelike_attr_label:str,
        timelike_attr_type:str,
        tvars:Dict[str,Dict[str,Any]]={}
        )->None:

        self.__tlike_label = timelike_attr_label
        self.__id = str(id(self))

        self.__root = root
        self.__root.command['adopt'].add(self.__id, self.__new_descendant_of_root, 'post')
        self.__root.command['leave'].add(self.__id, self.__leaving_of_descendant_of_root, 'pre')

        self.__timepoints:Dict[Any,Timepoint] = {}
        self.__times:List[Any] = list()
        self.__vars:Dict[str,Dict[str, Any]] = tvars

        self.__bindings:Dict[str, Binding] = dict()
        self.__attribute_factory = attribute_factory

        self.__init_point = self.create_timepoint(time=None, init=True)

    @property
    def timepoints(self)->Dict[str,Timepoint]: return self.__timepoints.copy()
    @property
    def var_info(self)->Dict[str,Dict[str,Any]]: return self.__vars.copy()
    @property
    def attrfac(self)->Attribute_Factory: return self.__attribute_factory
    @property
    def bindings(self)->Dict[str,Binding]: return self.__bindings.copy()

    def bind(self, dependent:str, func:Callable[[Any],Any], *free:str)->None:
        self.__bindings[dependent] = Binding(dependent, func, free)

    def create_timepoint(self, time:Any, init:bool=False)->Timepoint:
        vars = self.__create_vars()
        vars[''] = time
        if init: return self.__initital_timepoint(vars)
        else: return self.__regular_timepoint(vars)

    def __create_vars(self)->Dict[str,Attribute]:
        vars:Dict[str,Attribute] = {}
        var_info = self.var_info
        for label, info in var_info.items():
            vars[label] = self.attrfac.new_from_dict(**info)
        return vars

    def __initital_timepoint(self,vars:Dict[str,Attribute])->TimepointInit:
        return TimepointInit(vars)
    
    def __regular_timepoint(self,vars:Dict[str,Attribute])->TimepointRegular:
        tpoint = TimepointRegular(vars,self)
        self.__set_up_timepoint_bindings(tpoint)
        return tpoint
    
    def __set_up_timepoint_bindings(self, tpoint:TimepointRegular)->None:
        for b in self.__bindings.values():
            item_vars:List[Attribute_List] = list()
            for f in b.free: 
                if f[0]=='[' and f[-1]==']': 
                    f_label, f_type = f[1:-1].split(":")
                    tpoint._add_var_list(f_label, self.attrfac.newlist(f_type))
                item_vars.append(tpoint.item_var(f_label))
            
            time_index = self.__index_of_nearest_smaller(tpoint.var(''),self.__times)
            if time_index<0:
                prev_tpoint_var = self.__init_point.var(b.dependent)
            else:
                prev_tpoint_var = self.__timepoints[self.__times[time_index-1]].var(b.dependent)
            tpoint.var(b.dependent).add_dependency(b.func, prev_tpoint_var, *item_vars)

    def pick_point(self, time:Any)->Timepoint:
        previous_time_of_timepoint = self.__pick_timepoint_time(time)
        if previous_time_of_timepoint is None: return self.__init_point
        else: return self.__timepoints[previous_time_of_timepoint]

    def _add_timepoint(self,time:Any, timepoint:Timepoint)->None:
        if not self.__times: 
            self.__times.append(time)
        if time<min(self.__times): 
            self.__times.insert(0,time)
        elif time>max(self.__times): 
            self.__times.append(time)
        else: 
            Timeline.insert(time, self.__times)
        self.__timepoints[time] = timepoint
            
    def _remove_timepoint(self,time:Any)->None:
        self.__timepoints.pop(time)
        self.__times.remove(time)

    def __new_descendant_of_root(self, data:Parentage_Data)->Command:
        if not data.child.has_attribute(self.__tlike_label): 
            return Empty_Command()
        else: 
            return Add_Timepoint(
                Timepoint_Data(self,data.child,data.child(self.__tlike_label))
            )

    def __leaving_of_descendant_of_root(self, data:Parentage_Data)->Command:
        time = data.child(self.__tlike_label)
        return Remove_Timepoint(Timepoint_Data(self,data.child,time))
    
    def __pick_timepoint_time(self, time:Any)->Any:
        if not self.__times or time<self.__times[0]: 
            return None
        elif time==self.__times[0]:
            return self.__times[0]
        else:
            return self.__times[self.__index_of_nearest_smaller(time, self.__times)]
        
    def __call__(self,variable_label:str, time:Any)->Any:
        timepoint = self.pick_point(time)
        return timepoint(variable_label)
    
    @staticmethod
    def insert(x:Any, thelist:List[Any]):
        insertion_index = Timeline.__index_of_nearest_smaller(x,thelist)+1
        if insertion_index>=len(thelist):
            thelist.append(x)
        elif not x==thelist[insertion_index]: 
            thelist.insert(insertion_index, x)

    @staticmethod
    def __index_of_nearest_smaller(x:Any, thelist:List[Any])->int:
        if not thelist or x<=thelist[0]: 
            return -1
        elif thelist[-1]<=x: 
            return len(thelist)-1
        else:
            mid_index = int(len(thelist)/2)
            if x>thelist[mid_index]: 
                return mid_index
            else: 
                return 0


from typing import Set
import abc
class Timepoint(abc.ABC):
    def __init__(self, vars:Dict[str,Attribute])->None:
        self._items:Set[Item] = set()
        self.__vars = vars

    def __call__(self,var_label:str)->Any:
        return self.__vars[var_label].value

    def has_items(self)->bool: return bool(self._items)

    def var(self,label:str)->Attribute: return self.__vars[label]

    @abc.abstractmethod
    def _add_item(self,item:Item)->None: pass

    @abc.abstractmethod
    def _remove_item(self,item:Item)->None: pass

    @abc.abstractmethod
    def is_init(self)->bool: pass


class TimepointRegular(Timepoint):

    def __init__(self, vars:Dict[str,Attribute], timeline:Timeline)->None:
        super().__init__(vars)
        self.__item_var_lists:Dict[str, Attribute_List] = dict()

  
    def _add_var_list(self,label:str, varlist:Attribute_List)->None:
        self.__item_var_lists[label] = varlist

    def _add_item(self,item:Item)->None:
        self._items.add(item)
        for attr_label, attr in item.attributes.items():
            if attr_label in self.__item_var_lists: 
                self.__item_var_lists[attr_label].append(attr)
        
    def _remove_item(self,item:Item)->None:
        self._items.remove(item)

    def __append_to_var_list(self, item_var_label:str, item_var:Attribute)->None:
        self.__item_var_lists[item_var_label].append(item_var)

    def __remove_from_var_list(self, item_var_label:str, item_var:Attribute)->None:
        self.__item_var_lists[item_var_label].remove(item_var)

    def item_var(self,label:str)->Attribute_List:
        return self.__item_var_lists[label]

    def is_init(self)->bool: return False



class TimepointInit(Timepoint):

    def _add_item(self,item:Item)->None: raise TimepointInit.CannotAddItem
    def _remove_item(self,item:Item)->None: raise TimepointInit.No_Items_At_Init_Timepoint
    def is_init(self)->bool: return True

    class CannotAddItem(Exception): pass
    class No_Items_At_Init_Timepoint(Exception): pass