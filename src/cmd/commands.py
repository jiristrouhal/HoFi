from __future__ import annotations
import abc
from typing import List, Any, Callable, OrderedDict, Literal, Dict, Type, Tuple
import dataclasses


class Command(abc.ABC): # pragma: no cover
    def __init__(self, data:Any)->None: pass
    @abc.abstractmethod
    def run(self)->None: pass
    @abc.abstractmethod
    def undo(self)->None: pass
    @abc.abstractmethod
    def redo(self)->None: pass
    

class Controller:

    def __init__(self)->None:
        self.__undo_stack:List[List[Command]] = list()
        self.__redo_stack:List[List[Command]] = list()

    @property
    def any_undo(self)->bool: return bool(self.__undo_stack)
    @property
    def any_redo(self)->bool: return bool(self.__redo_stack)

    
    def run(self,*cmds:Command)->None:
        for cmd in cmds: cmd.run()
        self.__undo_stack.append(list(cmds))
        self.__redo_stack.clear()

    def undo(self)->None:
        if not self.__undo_stack: return 
        batch = self.__undo_stack.pop()    
        for cmd in reversed(batch): cmd.undo()
        self.__redo_stack.append(batch)

    def redo(self)->None:
        if not self.__redo_stack: return 
        batch = self.__redo_stack.pop()    
        for cmd in batch: cmd.redo()
        self.__undo_stack.append(batch)


@dataclasses.dataclass
class Command_Data(abc.ABC):
    def __init__(self,*args,**kwargs)->None: pass


Creators_Dict = OrderedDict[str, Callable]
Timing = Literal['before','after']


class External_Commands:

    def __init__(self,controller:Controller,options:Dict[str,Type[Command]])->None:
        self.__options = options
        self._controller = controller
        self.pre_cmd_creators:Dict[str,Creators_Dict] = {}
        self.post_cmd_creators:Dict[str,Creators_Dict] = {}
        for option in self.__options:
            self.pre_cmd_creators[option] = OrderedDict()
            self.post_cmd_creators[option] = OrderedDict()

    def add(
        self,
        on:str,
        owner_id:str, 
        command_creator:Callable[[Any], Command],
        timing:Timing
        )->None:

        self.__check_type_exists(on)
        cmd_dict = self.pre_cmd_creators if timing=="before" else self.post_cmd_creators
        cmd_dict[on][owner_id] = command_creator

    def run(self, on:str, data:Command_Data)->None:
        cmd = self._get_cmd(on,data)
        self._controller.run(
            *self.__get_cmds_before(on,data),
            cmd,
            *self.__get_cmds_after(on,data)
        )

    def __get_cmds_before(self, on:str, data:Command_Data)->Tuple[Command,...]:
        self.__check_type_exists(on)
        return tuple([cmd(data) for cmd in self.pre_cmd_creators[on].values()])
    
    def __get_cmds_after(self, on:str, data:Command_Data)->Tuple[Command,...]:
        self.__check_type_exists(on)
        return tuple([cmd(data) for cmd in self.post_cmd_creators[on].values()])
    
    def __check_type_exists(self,on:str)->None:
        if on not in self.__options: 
            raise KeyError(f"{on} not in the available command types ({self.__options.keys()}).")
        
    def _get_cmd(self,on:str,data:Command_Data)->Command:
        command_class = self.__options[on]
        return command_class(data)


class Composed_Command:

    @abc.abstractstaticmethod
    def cmd_type(*args)->Type[Command]: return Command

    def __init__(self,controller:Controller)->None:
        self.controller = controller
        self.pre:Dict[str,Callable[[Any],Command]] = dict()
        self.post:Dict[str,Callable[[Any],Command]] = dict()

    @abc.abstractmethod
    def execute(self,data:Any)->None:
        self.controller.run(
            *[p(data) for p in self.pre.values()],
            self.cmd_type()(data),
            *[p(data) for p in self.post.values()]
        )

    @abc.abstractmethod
    def add_pre(self, owner_id:str, creator_func:Callable[[Any],Command])->None:
        self.pre[owner_id] = creator_func

    @abc.abstractmethod
    def add_post(self, owner_id:str, creator_func:Callable[[Any],Command])->None:
        self.post[owner_id] = creator_func
