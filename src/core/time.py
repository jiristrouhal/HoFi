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


@dataclasses.dataclass
class Add_Item(Command):
    data:Timepoint_Data
    def run(self)->None:
        self.data.tline._add_item_tree(self.data.item)
    def undo(self)->None:
        self.data.tline._remove_item_tree(self.data.item)
    def redo(self)->None:
        self.data.tline._add_item_tree(self.data.item)


@dataclasses.dataclass
class Remove_Item(Command):
    data:Timepoint_Data
    def run(self)->None:
        self.data.tline._remove_item_tree(self.data.item)
    def undo(self)->None:
        self.data.tline._add_item_tree(self.data.item)
    def redo(self)->None:
        self.data.tline._remove_item_tree(self.data.item)


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

        self.__timelike_var = timelike_var_label
        self.__timelike_var_type = timelike_var_type
        self.__id = str(id(self))

        self.__timepoints:Dict[Any,TimepointRegular] = {}
        self.__times:List[Any] = list()
        self.__vars:Dict[str,Dict[str, Any]] = tvars

        self.__bindings:Dict[str, Binding] = dict()
        self.__attribute_factory = attribute_factory

        self.__init_tpoint = self.__create_initial_timepoint()
        self.__update_dependencies(self.__init_tpoint)

        self._add_item_tree(root)

    @property
    def timepoints(self)->Dict[Any,TimepointRegular]: return self.__timepoints.copy()
    @property
    def var_info(self)->Dict[str,Dict[str,Any]]: return self.__vars.copy()
    @property
    def attrfac(self)->Attribute_Factory: return self.__attribute_factory
    @property
    def timelike_var_label(self)->str: return self.__timelike_var
    @property
    def times(self)->List[str]: return self.__times.copy()

    def __adjust_timepoints_on_adoption(self, data:Parentage_Data)->Command:
        return Add_Item(Timepoint_Data(self, data.child))

    def __adjust_timepoints_on_leaving(self, data:Parentage_Data)->Command:
        return Remove_Item(Timepoint_Data(self,data.child))
    
    def _add_item_tree(self,item:Item)->None:
        self.__set_up_hierarchy_edit_commands(item)
        if self.__requires_timepoint(item): self._add_item(item)
        for child in item.children: self._add_item_tree(child)

    def _remove_item_tree(self, item:Item)->None:
        for child in item.children: self._remove_item_tree(child)
        if self.__requires_timepoint(item): self._remove_item(item)
        self.__clean_up_hierarchy_edit_commands(item)
    
    def __requires_timepoint(self, item:Item)->bool:
        if not item.has_attribute(self.__timelike_var): 
            return False
        elif item.attribute(self.__timelike_var).type != self.__timelike_var_type:
            raise Timeline.TimelikeVariableTypeConflict(
                f"Trying to add '{item.attribute('seconds').type}'"
                f"instead of '{self.__timelike_var_type}'."
            )
        return True
    
    def __clean_up_hierarchy_edit_commands(self,item:Item)->None:
        item.command['adopt'].post.pop(self.__id)
        item.command['leave'].pre.pop(self.__id)
    
    def __set_up_hierarchy_edit_commands(self,item:Item)->None:
        item.command['adopt'].add(self.__id, self.__adjust_timepoints_on_adoption, 'post')
        item.command['leave'].add(self.__id, self.__adjust_timepoints_on_leaving, 'pre')

    def bind(self, dependent:str, func:Callable[[Any],Any], *free:str)->None:
        if dependent not in self.__vars: raise Timeline.UndefinedVariable(dependent)
        self.__bindings[dependent] = Binding(dependent, func, free)
        self.__update_dependencies(self.__init_tpoint)
        for point in self.__timepoints.values():
            self.__update_dependencies(point)

    def pick_point(self, time:Any)->Timepoint:
        previous_time_of_timepoint = self.__pick_timepoint_time(time)
        if previous_time_of_timepoint is None: return self.__init_tpoint
        else: return self.__timepoints[previous_time_of_timepoint]
    
    def prev_timepoint(self, tpoint:Timepoint)->Timepoint:
        if tpoint is self.__init_tpoint: return self.__init_tpoint
        tpoint_time = tpoint.var('')
        tpoint_index = self.__times.index(tpoint_time)
        if tpoint_index==0:
            return self.__init_tpoint
        else:
            return self.__timepoints[self.__times[tpoint_index-1]]

    def next_timepoint(self, tpoint:Timepoint)->Timepoint|None:
        if tpoint==self.__init_tpoint and self.__timepoints: 
            return self.__timepoints[0]
        tpoint_index = self.__times.index(tpoint.var(''))
        if tpoint_index<len(self.__times)-1: 
            return self.__timepoints[self.__times[tpoint_index+1]]
        else: 
            return None

    def set_init(self, var_label:str,value:Any)->None:
        if var_label not in self.__vars: raise Timeline.UndefinedVariable(var_label)
        self.__init_tpoint.init_var(var_label).set(value)


    def _add_timepoint(self, timepoint:TimepointRegular)->None:
        time = timepoint.var('')
        Timeline.insert(time, self.__times)
        self.__timepoints[time] = timepoint
        next_timepoint = self.next_timepoint(timepoint)
        if next_timepoint is not None: 
            self.__update_dependencies(next_timepoint)
        self.__update_dependencies(timepoint)
            
    def _remove_timepoint(self,time:Any)->None:
        next_timepoint = self.next_timepoint(self.__timepoints[time])
        self.__timepoints.pop(time)
        self.__times.remove(time)
        if next_timepoint is not None: self.__update_dependencies(next_timepoint)

    def _add_item(self, item:Item, time:Any=None)->None:
        if time is None: time = item(self.timelike_var_label)
        if time not in self.__timepoints:
            tpoint = self.create_point(time)
            self._add_timepoint(tpoint)
        else:
            tpoint = self.__timepoints[time]
        tpoint._add_item(item)

    def _remove_item(self,item:Item,time:Any=None)->None:
        if time is None: time = item(self.timelike_var_label)
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
            vars[label] = self.attrfac.new_from_dict(**info, name=label)
        return vars

    def __initial_timepoint(self,vars:Dict[str,Attribute])->TimepointInit:
        return TimepointInit(vars,self)
    
    def __regular_timepoint(self,vars:Dict[str,Attribute])->TimepointRegular:
        return TimepointRegular(vars,self)

    def __update_dependencies(self, tpoint:Timepoint)->None:
        bounded_vars = [dep.output for dep in self.__bindings.values()]
        prev_tpoint = self.prev_timepoint(tpoint)
        for var in tpoint.vars:
            if var in bounded_vars: 
                self.__update_single_dependency(self.__bindings[var], tpoint, prev_tpoint)
            else: 
                self.__bind_to_prev_timepoint(var,tpoint,prev_tpoint)

    def __update_single_dependency(self, binding:Binding, tpoint:Timepoint, prev_tpoint:Timepoint)->None:
        self.__break_existing_dependency(tpoint.vars[binding.output])
        inputs = self.__collect_inputs(tpoint, *binding.input)
        tpoint.var(binding.output).add_dependency(
            binding.func, prev_tpoint.dep_var(binding.output), *inputs
        )

    def __bind_to_prev_timepoint(self, var_label:str, tpoint:Timepoint, prev_tpoint:Timepoint)->None:
        if not var_label=='' and not tpoint.var(var_label).dependent:
            tpoint.var(var_label).add_dependency(lambda var0: var0, prev_tpoint.dep_var(var_label))

    def __collect_inputs(self, timepoint:Timepoint, *free_var_labels:str)->List[AbstractAttribute]:
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
    @property
    def item_names(self)->List[str]: return [i.name for i in self._items]

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
        self.data.timeline._add_item(self.data.item)
    def undo(self)->None: 
        self.data.timeline._remove_item(self.data.item)
        self.data.timeline._add_item(self.data.item, self.prev_time)
    def redo(self)->None: 
        self.data.timeline._remove_item(self.data.item, self.prev_time)
        self.data.timeline._add_item(self.data.item)


class TimepointRegular(Timepoint):

    def __init__(self, vars:Dict[str,Attribute], timeline:Timeline)->None:
        super().__init__(vars)
        self.__timeline = timeline

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