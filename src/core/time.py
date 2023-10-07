from __future__ import annotations

import dataclasses
from typing import Dict, Any, Callable

from src.core.item import Item, Parentage_Data
from src.cmd.commands import Command, Empty_Command
from src.core.attributes import Attribute, Attribute_Factory, Attribute_List, AbstractAttribute
from src.core.attributes import Set_Attr_Data


@dataclasses.dataclass
class Timepoint_Data:
    tline:Timeline
    item:Item
    time:Any


@dataclasses.dataclass
class Add_Timepoint(Command):
    data:Timepoint_Data
    def run(self)->None:
        self.data.tline._add_item(self.data.item, self.data.time)
    def undo(self)->None:
        self.data.tline._remove_item(self.data.item, self.data.time)
    def redo(self)->None:
        self.data.tline._add_item(self.data.item, self.data.time)


@dataclasses.dataclass
class Remove_Timepoint(Command):
    data:Timepoint_Data
    def run(self)->None:
        self.data.tline._remove_item(self.data.item, self.data.time)
    def undo(self)->None:
        self.data.tline._add_item(self.data.item, self.data.time)
    def redo(self)->None:
        self.data.tline._remove_item(self.data.item, self.data.time)


from typing import Tuple, List
@dataclasses.dataclass(frozen=True)
class Binding:
    output:str
    func:Callable[[Any],Any]
    input:Tuple[str,...]


class Timeline:
    
    def __init__(
        self, 
        root:Item, 
        attribute_factory:Attribute_Factory,
        timelike_var_label:str,
        timelike_var_type:str,
        tvars:Dict[str,Dict[str,Any]]={}
        )->None:

        self.__timelike_var_label = timelike_var_label
        self.__timelike_var_type = timelike_var_type
        self.__id = str(id(self))

        self.__root = root
        self.__root.command['adopt'].add(self.__id, self.__new_descendant_of_root, 'post')
        self.__root.command['leave'].add(self.__id, self.__leaving_of_descendant_of_root, 'pre')

        self.__timepoints:Dict[Any,TimepointRegular] = {}
        self.__times:List[Any] = list()
        self.__vars:Dict[str,Dict[str, Any]] = tvars

        self.__bindings:Dict[str, Binding] = dict()
        self.__attribute_factory = attribute_factory

        self.__init_tpoint = self.__create_initial_timepoint()
        self.__set_up_init_timepoint_bindings()

    @property
    def timepoints(self)->Dict[Any,TimepointRegular]: return self.__timepoints.copy()
    @property
    def var_info(self)->Dict[str,Dict[str,Any]]: return self.__vars.copy()
    @property
    def attrfac(self)->Attribute_Factory: return self.__attribute_factory
    @property
    def timelike_var_label(self)->str: return self.__timelike_var_label

    def bind(self, dependent:str, func:Callable[[Any],Any], *free:str)->None:
        if dependent not in self.__vars: raise Timeline.UndefinedVariable(dependent)
        self.__bindings[dependent] = Binding(dependent, func, free)
        for point in self.__timepoints.values(): self.__set_up_timepoint_bindings(point)
        self.__set_up_init_timepoint_bindings()

    def pick_point(self, time:Any)->Timepoint:
        previous_time_of_timepoint = self.__pick_timepoint_time(time)
        if previous_time_of_timepoint is None: return self.__init_tpoint
        else: return self.__timepoints[previous_time_of_timepoint]

    def set_init(self, var_label:str,value:Any)->None:
        if var_label not in self.__vars: 
            raise Timeline.UndefinedVariable(var_label)
        self.__init_tpoint.init_var(var_label).set(value)


    def _add_timepoint(self,timepoint:TimepointRegular)->None:
        time = timepoint.var('')
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


    def _add_item(self,item:Item,time:Any)->None:
        if time not in self.__timepoints:
            tpoint = self.create_point(time)
            self._add_timepoint(tpoint)
        else:
            tpoint = self.__timepoints[time]
        tpoint._add_item(item)
    
    def _remove_item(self,item:Item,time:Any)->None:
        tpoint = self.__timepoints[time]
        tpoint._remove_item(item)
        if not tpoint.has_items(): self._remove_timepoint(time)


    def __create_initial_timepoint(self)->TimepointInit:
        vars = self.__create_vars()
        return self.__initial_timepoint(vars)

    def create_point(self, time:Any)->TimepointRegular:
        vars = self.__create_vars()
        vars[''] = time
        return self.__regular_timepoint(vars)

    def __break_existing_dependency(self, var:Attribute)->None:
        if var.dependent: var.break_dependency()

    def __create_vars(self)->Dict[str,Attribute]:
        vars:Dict[str,Attribute] = {}
        var_info = self.var_info
        for label, info in var_info.items():
            vars[label] = self.attrfac.new_from_dict(**info,name=label)
        return vars
    
    def __get_prev_timepoint(self, tpoint:TimepointRegular)->Timepoint:
        time_index = self._index_of_nearest_smaller(tpoint.var(''), self.__times)
        if time_index<0: return self.__init_tpoint
        else: return self.__timepoints[self.__times[time_index-1]]

    def __initial_timepoint(self,vars:Dict[str,Attribute])->TimepointInit:
        tpoint = TimepointInit(vars,self)
        return tpoint
    
    def __regular_timepoint(self,vars:Dict[str,Attribute])->TimepointRegular:
        tpoint = TimepointRegular(vars,self)
        self.__set_up_timepoint_bindings(tpoint)
        return tpoint
    
    def __set_up_timepoint_bindings(self, tpoint:TimepointRegular)->None:
        prev_tpoint = self.__get_prev_timepoint(tpoint)
        self.__set_dependencies(tpoint,prev_tpoint)
 
    def __set_up_init_timepoint_bindings(self)->None:
        self.__set_dependencies(self.__init_tpoint,self.__init_tpoint)

    def __set_dependencies(self, tpoint:Timepoint, prev_tpoint:Timepoint)->None:
        bound_var_labels = [dep.output for dep in self.__bindings.values()]
        for var_label in tpoint.vars:
            if var_label in bound_var_labels: 
                self.__apply_defined_dependencies(self.__bindings[var_label], tpoint, prev_tpoint)
            else: 
                self.__bind_to_prev_timepoint(var_label,tpoint,prev_tpoint)

    def __apply_defined_dependencies(self, binding:Binding, tpoint:Timepoint, prev_tpoint:Timepoint)->None:
        self.__break_existing_dependency(tpoint.vars[binding.output])
        free_vars = self.__collect_free_vars(tpoint, *binding.input)
        tpoint.var(binding.output).add_dependency(
            binding.func, prev_tpoint.dep_var(binding.output), *free_vars
        )

    def __bind_to_prev_timepoint(self, var_label:str, tpoint:Timepoint, prev_tpoint:Timepoint)->None:
        if not var_label=='' and not tpoint.var(var_label).dependent:
            tpoint.var(var_label).add_dependency(lambda var0: var0, prev_tpoint.dep_var(var_label))

    def __collect_free_vars(self, timepoint:Timepoint, *free_var_labels:str)->List[AbstractAttribute]:
        free_vars:List[AbstractAttribute] = list()
        for f in free_var_labels: 
            if f[0]=='[' and f[-1]==']': 
                f_label, f_type = self.__extract_item_variable_label_and_type(f)
                timepoint._add_var_list(f_label, self.attrfac.newlist(f_type))
                free_vars.append(timepoint.item_var(f_label))
            else:
                free_vars.append(timepoint.dep_var(f))
        return free_vars
    
    @staticmethod
    def __extract_item_variable_label_and_type(text:str)->Tuple[str,str]:
        if ":" not in text: 
            raise Timeline.MissingItemVariableType(text)
        f_label, f_type = text[1:-1].split(":")
        if f_label.strip()=="": 
            raise Timeline.MissingItemVariableLabel(text)
        if f_type.strip()=="": 
            raise Timeline.MissingItemVariableType(text)
        return f_label, f_type

    def __new_descendant_of_root(self, data:Parentage_Data)->Command:
        if not data.child.has_attribute(self.__timelike_var_label): 
            return Empty_Command()
        elif data.child.attribute(self.__timelike_var_label).type != self.__timelike_var_type:
            raise Timeline.TimelikeVariableTypeConflict(
                f"Trying to add '{data.child.attribute('seconds').type}'"
                "instead of '{self.__timelike_var_type}'."
            )
        else: 
            return Add_Timepoint(
                Timepoint_Data(self,data.child, data.child(self.__timelike_var_label))
            )

    def __leaving_of_descendant_of_root(self, data:Parentage_Data)->Command:
        time = data.child(self.__timelike_var_label)
        return Remove_Timepoint(Timepoint_Data(self,data.child,time))
    
    def __pick_timepoint_time(self, time:Any)->Any:
        time_index = self._index_of_nearest_smaller_or_equal(time, self.__times)
        if time_index<0: return None
        else: return self.__times[time_index]

    def __call__(self,variable_label:str, time:Any)->Any:
        timepoint = self.pick_point(time)
        return timepoint(variable_label)
    
    @staticmethod
    def insert(x:Any, thelist:List[Any]):
        insertion_index = Timeline._index_of_nearest_smaller(x,thelist)+1
        if insertion_index>=len(thelist):
            thelist.append(x)
        elif not x==thelist[insertion_index]: 
            thelist.insert(insertion_index, x)

    @staticmethod
    def _index_of_nearest_smaller(x:Any, thelist:List[Any], start:int=0)->int:
        if not thelist: return -1
        elif x<=thelist[0]: return -1 + start
        elif x>thelist[-1]: return len(thelist)-1 + start
        else:
            m = int((len(thelist)+1)/2)
            if x==thelist[m]: return m-1 + start
            elif x>thelist[m]: return Timeline._index_of_nearest_smaller(x,thelist[m:],m)
            else: return Timeline._index_of_nearest_smaller(x,thelist[:m],start)

    @staticmethod
    def _index_of_nearest_smaller_or_equal(x:Any, thelist:List[Any], start:int=0)->int:
        if not thelist: return -1
        elif x==thelist[0]: return start
        elif x<thelist[0]: return -1 + start
        elif x>thelist[-1]: return len(thelist)-1 + start
        else:
            m = int((len(thelist)+1)/2)
            if x==thelist[m]: return m + start
            elif x>thelist[m]: return Timeline._index_of_nearest_smaller_or_equal(x,thelist[m:],m)
            else: return Timeline._index_of_nearest_smaller_or_equal(x,thelist[:m],start)
            
    class MissingItemVariableLabel(Exception):pass
    class MissingItemVariableType(Exception): pass
    class TimelikeVariableTypeConflict(Exception): pass
    class UndefinedVariable(Exception): pass


from typing import Set
import abc
class Timepoint(abc.ABC): 
    def __init__(self, vars:Dict[str,Attribute])->None:
        self._items:Set[Item] = set()
        self.__vars = vars
        self._item_var_lists:Dict[str, Attribute_List] = dict()

    @property
    def vars(self)->Dict[str,Attribute]: return self.__vars.copy()

    def __call__(self,var_label:str)->Any:
        return self.__vars[var_label].value

    def has_items(self)->bool: return bool(self._items)

    def var(self,label:str)->Attribute: 
        return self.__vars[label]
    
    @abc.abstractmethod
    def dep_var(self,label:str)->Attribute: pass # pragma: no cover

    @abc.abstractmethod
    def _add_item(self,item:Item)->None: pass # pragma: no cover

    def _add_var_list(self,label:str, varlist:Attribute_List)->None:
        self._item_var_lists[label] = varlist

    def item_var(self,label:str)->Attribute_List:
        return self._item_var_lists[label]

    @abc.abstractmethod
    def _remove_item(self,item:Item)->None: pass # pragma: no cover

    @abc.abstractmethod
    def is_init(self)->bool: pass # pragma: no cover


@dataclasses.dataclass
class Moving_In_Time_Data:
    timeline:Timeline
    tpoint:TimepointRegular
    item:Item


@dataclasses.dataclass
class Move_Item_In_Time(Command):
    data:Moving_In_Time_Data
    prev_time:Any = dataclasses.field(init=False)
    new_time:Any = dataclasses.field(init=False)
    def run(self)->None: 
        self.prev_time = self.data.tpoint.var('')
        self.new_time = self.data.item(self.data.timeline.timelike_var_label)
        self.data.timeline._remove_item(self.data.item, self.prev_time)
        self.data.timeline._add_item(self.data.item, self.new_time)
    def undo(self)->None: 
        self.data.timeline._remove_item(self.data.item, self.new_time)
        self.data.timeline._add_item(self.data.item, self.prev_time)
    def redo(self)->None: 
        self.data.timeline._remove_item(self.data.item, self.prev_time)
        self.data.timeline._add_item(self.data.item, self.new_time)


@dataclasses.dataclass
class Remove_Old_And_Create_New_Timepoint(Command):
    data:Moving_In_Time_Data
    def run(self)->None:
        # remove item from timepoint, remove timepoint
        self.data.tpoint._remove_item(self.data.item)
        if not self.data.tpoint.has_items():
            self.data.timeline._remove_timepoint(self.data.tpoint.var(''))
        # add new timepoint, add item to it
        new_tpoint = self.data.timeline.create_point(self.data.item(self.data.timeline.timelike_var_label))
        self.data.timeline._add_timepoint(new_tpoint)
        new_tpoint._add_item(self.data.item)
    
    def undo(self)->None:
        pass
    def redo(self)->None:
        pass


class TimepointRegular(Timepoint):

    def __init__(self, vars:Dict[str,Attribute], timeline:Timeline)->None:
        super().__init__(vars)
        self.__timeline = timeline

    @property
    def n_items(self)->int: return len(self._items)

    def dep_var(self, label:str)->Attribute: return self.var(label)

    def _add_item(self,item:Item)->None:
        self._items.add(item)
        for attr_label, attr in item.attributes.items():
            if attr_label in self._item_var_lists: 
                self._item_var_lists[attr_label].append(attr)

        def move_in_time(data:Set_Attr_Data)->Command:
            return Move_Item_In_Time(Moving_In_Time_Data(self.__timeline,self,item))

        item.attribute(self.__timeline.timelike_var_label).command['set'].add(
            'timeline', move_in_time, timing='post'
        )
        
    def _remove_item(self,item:Item)->None:
        self._items.remove(item)

    def is_init(self)->bool: return False



class TimepointInit(Timepoint):

    def __init__(self, vars:Dict[str,Attribute], timeline:Timeline)->None:
        super().__init__(vars)
        self.__init_vars:Dict[str,Attribute] = {label:var.copy() for label,var in vars.items()}

    def _add_item(self,item:Item)->None: raise TimepointInit.CannotAddItem
    def _remove_item(self,item:Item)->None: raise TimepointInit.No_Items_At_Init_Timepoint
    def is_init(self)->bool: return True

    def dep_var(self, label: str) -> Attribute:
        return self.__init_vars[label]
    
    def init_var(self,label:str)->Attribute: 
        return self.__init_vars[label]

    class CannotAddItem(Exception): pass
    class No_Items_At_Init_Timepoint(Exception): pass