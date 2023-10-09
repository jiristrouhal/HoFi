from __future__ import annotations

import dataclasses
from typing import Dict, Any, Callable

from src.core.item import Item, Parentage_Data
from src.cmd.commands import Command
from src.core.attributes import Attribute, Attribute_Factory, Attribute_List, AbstractAttribute


@dataclasses.dataclass(frozen=True)
class Timepoint_Data:
    tline:Timeline
    item:Item


@dataclasses.dataclass(frozen=True)
class Add_Item(Command):
    data:Timepoint_Data
    def run(self)->None:
        self.data.tline._add_item_tree_to_timeline(self.data.item)
    def undo(self)->None:
        self.data.tline._remove_item_tree(self.data.item)
    def redo(self)->None:
        self.data.tline._add_item_tree_to_timeline(self.data.item)


@dataclasses.dataclass(frozen=True)
class Remove_Item(Command):
    data:Timepoint_Data
    def run(self)->None:
        self.data.tline._remove_item_tree(self.data.item)
    def undo(self)->None:
        self.data.tline._add_item_tree_to_timeline(self.data.item)
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

        self.__timename = timelike_var_label
        self.__time_type = timelike_var_type
        self.__id = str(id(self))

        self.__points:Dict[Any,TimepointRegular] = {}
        self.__time:List[Any] = list()
        self.__vars:Dict[str,Dict[str, Any]] = tvars

        self.__bindings:Dict[str, Binding] = {
            var_label:Binding(var_label, lambda x:x, ()) for var_label in self.__vars
        }
        self.__attribute_factory = attribute_factory

        self.__init_point = TimepointInit(self.__create_vars(), self)
        self.__update_dependencies(self.__init_point)

        self._add_item_tree_to_timeline(root)

    @property
    def id(self)->str: return self.__id
    @property
    def points(self)->Dict[Any,TimepointRegular]: return self.__points.copy()
    @property
    def var_info(self)->Dict[str,Dict[str,Any]]: return self.__vars.copy()
    @property
    def attrfac(self)->Attribute_Factory: return self.__attribute_factory
    @property
    def timename(self)->str: return self.__timename
    @property
    def time(self)->List[str]: return self.__time.copy()
    @property
    def bindings(self)->Dict[str,Binding]: return self.__bindings.copy()


    def bind(self, dependent:str, func:Callable[[Any],Any], *free:str)->None:
        if dependent not in self.__vars: 
            raise Timeline.UndefinedVariable(dependent)
        self.__bindings[dependent] = Binding(dependent, func, free)
        self.__set_dependency(dependent, self.__init_point, self.__init_point)
        for point in self.__points.values():
            self.__set_dependency(dependent, point, self.prev_point(point))

    def pick_point(self, time:Any)->Timepoint:
        last_point_time = self.__pick_timepoint_time(time)
        if last_point_time is None: return self.__init_point
        else: return self.__points[last_point_time]

    def set_init(self, var_label:str,value:Any)->None:
        if var_label not in self.__vars: raise Timeline.UndefinedVariable(var_label)
        self.__init_point.init_var(var_label).set(value)


    def _add_item_tree_to_timeline(self,item:Item)->None:
        self.__set_up_hierarchy_edit_commands(item)
        if self.__has_time(item): self._add_item_to_timeline(item)
        for child in item.children: self._add_item_tree_to_timeline(child)

    def _add_item_to_timeline(self, item:Item, time:Any=None)->None:
        if time is None: time = item(self.timename)
        if time not in self.__points:
            point = self._create_point(time)
        else:
            point = self.__points[time]
        point._add_item(item)

    def _create_point(self, time:Any)->TimepointRegular:
        point = self.__new_timepoint(time)
        self.__update_dependencies_of_next_point(point)
        self.__update_dependencies(point)
        return point


    def _remove_item_tree(self, item:Item)->None:
        for child in item.children: self._remove_item_tree(child)
        if self.__has_time(item): self._remove_item_from_timeline(item)
        self.__clean_up_hierarchy_edit_commands(item)

    def _remove_item_from_timeline(self,item:Item,time:Any=None)->None:
        if time is None: time = item(self.timename)
        tpoint = self.__points[time]
        tpoint._remove_item(item)
        if not tpoint.has_items(): self._remove_timepoint(time)

    def _remove_timepoint(self,time:Any)->None:
        next_timepoint = self.next_point(self.__points[time])
        self.__points.pop(time)
        self.__time.remove(time)
        if next_timepoint is not None: self.__update_dependencies(next_timepoint)

    def __new_timepoint(self, time:Any)->TimepointRegular:
        vars = self.__create_vars()
        vars[self.__timename] = time
        Timeline.insert(time, self.__time)
        self.__points[time] = TimepointRegular(vars,self)
        return self.__points[time]

    def prev_point(self, point:Timepoint)->Timepoint:
        if point is self.__init_point: return self.__init_point
        point_time = point.time
        i = self.__time.index(point_time)
        if i==0: return self.__init_point
        else: return self.__points[self.__time[i-1]]

    def next_point(self, point:Timepoint)->Timepoint|None:
        if point==self.__init_point and self.__points: 
            return self.__points[0]
        i = self.__time.index(point.time)
        if i<len(self.__time)-1: 
            return self.__points[self.__time[i+1]]
        else: 
            return None

    def __has_time(self, item:Item)->bool:
        if not item.has_attribute(self.__timename): 
            return False
        elif item.attribute(self.__timename).type != self.__time_type:
            raise Timeline.TimelikeVariableTypeConflict(
                f"Trying to add '{item.attribute('seconds').type}'"
                f"instead of '{self.__time_type}'."
            )
        return True
    
    def __clean_up_hierarchy_edit_commands(self,item:Item)->None:
        item.command['adopt'].post.pop(self.__id)
        item.command['leave'].pre.pop(self.__id)
    
    def __set_up_hierarchy_edit_commands(self,item:Item)->None:
        def __adopt(data:Parentage_Data): return Add_Item(Timepoint_Data(self, data.child))
        def __leave(data:Parentage_Data): return Remove_Item(Timepoint_Data(self,data.child))
        item.command['adopt'].add(self.__id, __adopt, 'post')
        item.command['leave'].add(self.__id, __leave, 'pre')

    def __create_vars(self)->Dict[str,Attribute]:
        vars:Dict[str,Attribute] = {}
        var_info = self.var_info
        for label, info in var_info.items():
            vars[label] = self.attrfac.new_from_dict(**info, name=label)
        return vars
    
    def __update_dependencies(self, point:Timepoint)->None:
        prev_point = self.prev_point(point)
        for label in point.vars:
            if label==self.__timename: continue
            self.__set_dependency(label, point, prev_point)

    def __update_dependencies_of_next_point(self, point:TimepointRegular)->None:
        next_point = self.next_point(point)
        if next_point is not None: 
            self.__update_dependencies(next_point)

    def __set_dependency(self, var_label:str, point:Timepoint, prev_point:Timepoint)->None:
        b = self.__bindings[var_label]
        x = self.__collect_inputs(point, *b.input)
        y = point.var(b.output)
        y0 = prev_point.dep_var(b.output)
        if y.dependent: y.break_dependency()
        y.add_dependency(b.func, y0, *x)

    def __collect_inputs(self, timepoint:Timepoint, *input_labels:str)->List[AbstractAttribute]:
        inputs:List[AbstractAttribute] = list()
        for f in input_labels: 
            if f[0]=='[' and f[-1]==']': 
                f_label, f_type = self.__extract_item_variable_label_and_type(f)
                timepoint._add_var_list(f_label, self.attrfac.newlist(f_type,name=f_label))
                inputs.append(timepoint.item_var(f_label))
            else:
                inputs.append(timepoint.dep_var(f))
        return inputs
    
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
        time_index = self._index_of_nearest_smaller_or_equal(time, self.__time)
        if time_index<0: return None
        else: return self.__time[time_index]

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
    @abc.abstractproperty
    def time(self)->Any: pass

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
        self.prev_time = self.data.tpoint.time
        self.new_time = self.data.item(self.data.timeline.timename)
        self.data.timeline._remove_item_from_timeline(self.data.item, self.prev_time)
        self.data.timeline._add_item_to_timeline(self.data.item)
    def undo(self)->None: 
        self.data.timeline._remove_item_from_timeline(self.data.item)
        self.data.timeline._add_item_to_timeline(self.data.item, self.prev_time)
    def redo(self)->None: 
        self.data.timeline._remove_item_from_timeline(self.data.item, self.prev_time)
        self.data.timeline._add_item_to_timeline(self.data.item)


class TimepointRegular(Timepoint):

    def __init__(self, vars:Dict[str,Attribute], timeline:Timeline)->None:
        super().__init__(vars)
        self.__timeline = timeline

    @property
    def time(self)->Any: return self.vars[self.__timeline.timename]

    def dep_var(self, label:str)->Attribute: return self.var(label)

    def _add_item(self,item:Item)->None:
        self._items.add(item)
        for attr_label, attr in item.attributes.items():
            if attr_label in self._item_var_lists: 
                self._item_var_lists[attr_label].append(attr)

        def move_in_time(*args)->Command:
            return Move_Item_In_Time(Moving_In_Time_Data(self.__timeline,self,item))

        item.attribute(self.__timeline.timename).command['set'].add(
            'timeline', move_in_time, timing='post'
        )
        
    def _remove_item(self,item:Item)->None:
        self._items.remove(item)

    def is_init(self)->bool: return False



class TimepointInit(Timepoint):

    def __init__(self, vars:Dict[str,Attribute], timeline:Timeline)->None:
        super().__init__(vars)
        self.__init_vars:Dict[str,Attribute] = {label:var.copy() for label,var in vars.items()}

    @property
    def time(self)->Any: return None

    def _add_item(self,item:Item)->None: raise TimepointInit.CannotAddItem
    def _remove_item(self,item:Item)->None: raise TimepointInit.No_Items_At_Init_Timepoint
    def is_init(self)->bool: return True

    def dep_var(self, label: str) -> Attribute:
        return self.__init_vars[label]
    
    def init_var(self,label:str)->Attribute: 
        return self.__init_vars[label]

    class CannotAddItem(Exception): pass
    class No_Items_At_Init_Timepoint(Exception): pass