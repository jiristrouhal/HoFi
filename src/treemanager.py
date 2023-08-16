
from typing import List, Dict, Callable, Any, Literal
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsg
import tkinter.filedialog as filedialog
import enum
from functools import partial
import os
import sys

sys.path.insert(1,"src")


import src.tree_to_xml as txml
import src.treelist as treelist
import src.tree as treemod
import right_click_menu as rcm


NAME_ALREADY_TAKEN_TITLE = "Name already exists"
NAME_ALREADY_TAKEN_MESSAGE_1 = "A tree with the name "
NAME_ALREADY_TAKEN_MESSAGE_2 = " already exists. Use different name."


TREE_MANAGER_TITLE = "Tree Manager"
SET_NEW_TREE_NAME = "Set new tree name"
RENAME_TREE = "Rename tree"

MENU_CMD_TREE_RENAME = "Rename"
MENU_CMD_TREE_EXPORT = "Export"
MENU_CMD_TREE_UPDATE_FILE = "Update file"
MENU_CMD_TREE_DELETE = "Delete"
MENU_CMD_TREE_NEW = "New"
MENU_CMD_TREE_LOAD = "Load"
MENU_CMD_TREE_SELECT = "Select"
MENU_CMD_TREE_DESELECT = "Deselect"

FILEDIALOG_EXPORT_TITLE = "Export tree into file"
FILEDIALOG_LOAD_TITLE = "Load tree from file"

MSGBOX_ASK_TO_DELETE_TREE_TITLE = "Delete tree"
MSGBOX_ASK_TO_DELETE_TREE_MSG_1 = "Do you really want to delete '"
MSGBOX_ASK_TO_DELETE_TREE_MSG_2 = "?"

MSGBOX_ASK_TO_RENAME_TREE_TITLE = "File already exists"
MSGBOX_ASK_TO_RENAME_TREE_MSG_1 = "The file with name '"
MSGBOX_ASK_TO_RENAME_TREE_MSG_2 = \
"' already exists in the directory. Click 'OK' to specify other name for the saved tree \
or 'Cancel' to cancel the export."


MSGBOX_TREE_WAS_NOT_YET_EXPORTED_TITLE = "Export required"
MSGBOX_TREE_WAS_NOT_YET_EXPORTED_MSG_1 = "No file is yet connected to the '"
MSGBOX_TREE_WAS_NOT_YET_EXPORTED_MSG_2 = "'. Export is required first."

MSGBOX_FILE_ALREADY_USED_TITLE = "File already used by tree"
MSGBOX_FILE_ALREADY_USED_MSG_1 = "The file '"
MSGBOX_FILE_ALREADY_USED_MSG_2 = "' is already used by '"
MSGBOX_FILE_ALREADY_USED_MSG_3 = "'. To proceed, use a copy of the file you want to load."

INFO_TREE_EXPORTED_TITLE = "Tree export"
INFO_TREE_EXPORTED_MSG_1 = "'"
INFO_TREE_EXPORTED_MSG_2 = "' was exported into '"
INFO_TREE_EXPORTED_MSG_3 = "'."

SELECTED_TREE_CANNOT_BE_DELETED_TITLE = "Cannot deleted selected tree"
SELECTED_TREE_CANNOT_BE_DELETED_MSG_1 = "Please unselect the '"
SELECTED_TREE_CANNOT_BE_DELETED_MSG_2 = "' before deletion."

DEFAULT_TREE_NAME = "New"


class ButtonID(enum.Enum):
    NEW_TREE = enum.auto()
    LOAD_TREE = enum.auto()
    NEW_TREE_OK = enum.auto()
    NEW_TREE_CANCEL = enum.auto()
    RENAME_TREE_OK = enum.auto()
    RENAME_TREE_CANCEL = enum.auto()



BUTTONTEXT:Dict[ButtonID,str] = {
    ButtonID.NEW_TREE: "New",
    ButtonID.LOAD_TREE: "Load",
    ButtonID.NEW_TREE_OK: "OK",
    ButtonID.NEW_TREE_CANCEL: "Cancel",
    ButtonID.RENAME_TREE_OK: "OK",
    ButtonID.RENAME_TREE_CANCEL: "Cancel",
}


class Tree_Manager:

    def __init__(self,treelist:treelist.TreeList,ui_master:tk.Frame|tk.Tk|None = None, )->None:
        self.__converter = txml.Tree_XML_Converter()
        self.__ui = ttk.LabelFrame(master=ui_master,text=TREE_MANAGER_TITLE)
        self._buttons:Dict[ButtonID,tk.Button] = dict()
        self._view = ttk.Treeview(self.__ui, selectmode='browse')
        self._map:Dict[str,treemod.Tree] = dict()

        self._window_new = tk.Toplevel(self._view)
        self._window_new.wm_withdraw()
        self._entry_name = tk.Entry()

        self._window_rename = tk.Toplevel()
        self._window_rename.wm_withdraw()

        self._bind_keys()
        self.__configure_ui()

        self.__on_selection:List[Callable[[treemod.Tree],None]] = list()
        self.__on_deselection:List[Callable[[treemod.Tree],None]] = list()
        
        self.__treelist = treelist
        self.__treelist.add_name_warning(self._error_if_tree_names_already_taken)
        self.__treelist.add_action_on_adding(self.__add_tree_to_view)
        self.__treelist.add_action_on_removal(self.__remove_tree_from_view)
        self.__treelist.add_action_on_renaming(self.__rename_tree_in_view)

        self.right_click_menu = rcm.RCMenu(self._view)
        self._last_export_dir:str = "."

        self._tree_files:Dict[treemod.Tree,str] = dict()
        self._selected_trees:List[treemod.Tree] = list()

    @property
    def trees(self)->List[str]: return self.__treelist.names

    def add_action_on_selection(self,action:Callable[[treemod.Tree],None])->None:
        if action not in self.__on_selection:
            self.__on_selection.append(action)

    def add_action_on_deselection(self,action:Callable[[treemod.Tree],None])->None:
        if action not in self.__on_deselection:
            self.__on_deselection.append(action)

    def new(self,name:str,tag:str=treemod.DEFAULT_TAG,attributes:Dict[str,Any]={})->None: 
        tree = treemod.Tree(name,tag=tag,attributes=attributes)
        self.__treelist.append(tree)
        tree.add_data("treemanager_id",str(id(tree)))

    def right_click_item(self,event:tk.Event)->None: # pragma: no cover
        item_id = self._view.identify_row(event.y)
        self._open_right_click_menu(item_id)
        self.right_click_menu.tk_popup(x=event.x_root,y=event.y_root)

    def _open_right_click_menu(self,item_id:str)->None:
        if item_id.strip()=="": self._open_right_click_menu_for_manager()
        else: self._open_right_click_menu_for_item(item_id)

    def _open_right_click_menu_for_manager(self)->None:
        self.right_click_menu = rcm.RCMenu(master=self._view, tearoff=False)
        self.right_click_menu.add_commands(
            {
                MENU_CMD_TREE_NEW : self._open_new_tree_window,
                MENU_CMD_TREE_LOAD: self._load_tree
            }
        )

    def _open_right_click_menu_for_item(self,item_id:str)->None:
        self.right_click_menu = rcm.RCMenu(master=self._view, tearoff=False)
        tree = self._map[item_id]
        if tree in self._selected_trees:
            self.right_click_menu.add_single_command(
                MENU_CMD_TREE_DESELECT, partial(self._deselect,item_id)
            )
        else:
            self.right_click_menu.add_single_command(
                MENU_CMD_TREE_SELECT, partial(self._select,item_id)
            )
        self.right_click_menu.add_separator()
        self.right_click_menu.add_single_command(
            MENU_CMD_TREE_RENAME,partial(self._open_rename_tree_window,tree)
        )
        if tree in self._tree_files:
            self.right_click_menu.add_single_command(
                MENU_CMD_TREE_UPDATE_FILE, partial(self._update_file,tree)
            )

        self.right_click_menu.add_single_command(
            MENU_CMD_TREE_EXPORT,partial(self._export_tree,tree)
        )
        self.right_click_menu.add_separator()
        self.right_click_menu.add_single_command(
            MENU_CMD_TREE_DELETE, partial(self._remove_tree,tree)
        )

    def _get_filepath(self)->str:
        return filedialog.askopenfilename(   # pragma: no cover
            title=FILEDIALOG_LOAD_TITLE,
            filetypes=(('XML file','.xml'),),
            defaultextension='.xml',
            initialdir=self._last_export_dir,
        )
    
    def _select(self,tree_id:str)->None:
        tree = self._map[tree_id]
        if not self.tree_exists(tree.name): return
        if tree in self._selected_trees: return
        self._selected_trees.append(tree)
        for action in self.__on_selection:
            action(tree)

    def _deselect(self,tree_id:str)->None:
        tree = self._map[tree_id]
        if not self.tree_exists(tree.name): return
        if tree not in self._selected_trees: return
        self._selected_trees.remove(tree)
        for action in self.__on_deselection:
            action(tree)

    def _load_tree(self,)->None:
        filepath = self._get_filepath()
        if filepath.strip()=="": 
            return
        dir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        treename = os.path.splitext(filename)[0]
        if self.__file_already_in_use(filepath): 
            return 
        tree = self.__converter.load_tree(treename,dir)
        if tree is None: return
        self._tree_files[tree] = filepath
        self.__treelist.append(tree)

    def __file_already_in_use(self, file_to_be_loaded:str)->bool:
        for tree,filepath in self._tree_files.items():
            if os.path.samefile(filepath,file_to_be_loaded): 
                self._show_error_file_already_in_use(filepath,tree.name)
                return True
        return False
        
    def _export_tree(self,tree:treemod.Tree)->None:
        dir = self._ask_for_directory()
        if dir.strip()=='': # directory selection has been cancelled
            return
        
        if not self._xml_already_exists(dir,tree.name):
            filepath = self.__converter.save_tree(tree,dir)
            self._show_export_info(tree.name,filepath)
            self._tree_files[tree] = os.path.join(dir,tree.name)+'.xml'
            self._last_export_dir = dir

        elif self._confirm_renaming_if_exported_file_already_exists(tree.name): 
            self._open_rename_tree_window(tree)
        
    @staticmethod
    def _xml_already_exists(dir:str,tree_name:str)->bool:
        file_path = os.path.join(dir,tree_name)+".xml"
        return os.path.isfile(file_path)
    
    def _update_file(self,tree:treemod.Tree)->None:
        if tree not in self._tree_files: 
            self._notify_tree_has_not_been_exported(tree.name)
            self._export_tree(tree)
            return
        
        filepath = self._tree_files[tree]
        dir = os.path.dirname(filepath)
        filename_without_extension = os.path.splitext(os.path.basename(filepath))[0]
        if os.path.isfile(filepath): 
            if not tree.name==filename_without_extension:
                os.remove(filepath)
        new_filepath = self.__converter.save_tree(tree,dir)
        self._tree_files[tree] = new_filepath

    def _remove_tree(self,tree:treemod.Tree)->None:
        # The user has to deselect tree to be able to delete it
        if tree in self._selected_trees: 
            self._notify_the_user_selected_tree_cannot_be_deleted(tree.name)
        elif self._removal_confirmed(tree.name): 
            if tree in self._tree_files: self._tree_files.pop(tree)
            self.__treelist.remove(tree.name)

    def __add_button(
        self, 
        master: tk.Frame, 
        id:ButtonID, 
        command:Callable[[],None], 
        side:Literal['left','right','top','bottom']
        )->None:
        
        self._buttons[id] = tk.Button(master,text=BUTTONTEXT[id],command=command)
        self._buttons[id].pack(side=side)

    def _open_rename_tree_window(self,tree:treemod.Tree)->None: # pragma: no cover
        self.__cleanup_rename_tree_widgets()
        self._window_rename = tk.Toplevel(self.__ui)
        self._window_rename.title(RENAME_TREE)
        self._entry_name = tk.Entry(self._window_rename,width=50)
        self._entry_name.pack()
        self._entry_name.insert(0,tree.name)

        button_frame = tk.Frame(self._window_rename)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(button_frame,ButtonID.RENAME_TREE_OK,partial(self._confirm_rename,tree),side='left')
        self.__add_button(button_frame,ButtonID.RENAME_TREE_CANCEL,self.__close_rename_tree_window,side='left')
        
    def _open_new_tree_window(self)->None: # pragma: no cover
        self.__cleanup_new_tree_widgets()
        self._window_new = tk.Toplevel(self.__ui)
        self._window_new.title(SET_NEW_TREE_NAME)
        self._entry_name = tk.Entry(self._window_new,width=50)
        self._entry_name.insert(0,DEFAULT_TREE_NAME)
        self._entry_name.pack()
        
        button_frame = tk.Frame(self._window_new)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(button_frame,ButtonID.NEW_TREE_OK,self._confirm_new_tree_name,side='left')
        self.__add_button(button_frame,ButtonID.NEW_TREE_CANCEL,self.__close_new_tree_window,side='left')

    def _confirm_rename(self,tree:treemod.Tree)->None:
        new_name = self._entry_name.get()
        if self.tree_exists(new_name) and self.get_tree(new_name) is not tree: 
            self._error_if_tree_names_already_taken(new_name)
        else:
            self.__treelist.rename(tree.name,self._entry_name.get())
            self.__close_rename_tree_window()

    def _confirm_new_tree_name(self)->None:
        self.new(self._entry_name.get())
        self.__close_new_tree_window()

    def __close_rename_tree_window(self)->None:
        self.__cleanup_rename_tree_widgets()

    def __close_new_tree_window(self)->None:
        self.__cleanup_new_tree_widgets()

    def __cleanup_new_tree_widgets(self)->None:
        self._window_new.destroy()
        self._entry_name.destroy()

    def __cleanup_rename_tree_widgets(self)->None:
        self._window_rename.destroy()
        self._entry_name.destroy()

    def __add_tree_to_view(self,tree:treemod.Tree)->None:
        iid = self._view.insert("",0,text=tree.name,iid=str(id(tree)))
        self._map[iid] = tree

    def __remove_tree_from_view(self,tree:treemod.Tree)->None:
        item_id = str(id(tree))
        self._view.delete(item_id)

    def __rename_tree_in_view(self,tree:treemod.Tree)->None:
        item_id = str(id(tree))
        self._view.item(item_id,text=tree.name)

    def get_tree(self,name:str)->treemod.Tree|None:
        return self.__treelist.item(name)

    def _set_tree_attribute(self,name:str,key:str,value:str)->None:
        tree = self.get_tree(name)
        if tree is None: return
        if key in tree.attributes:
            tree._attributes[key] = value

    def rename(self,old_name:str,new_name:str)->None:
        self.__treelist.rename(old_name,new_name)

    def tree_exists(self,name:str)->bool: 
        return name in self.trees
    

    def _ask_for_directory(self)->str:  # pragma: no cover
        return filedialog.askdirectory(
                initialdir=self._last_export_dir,
                title = FILEDIALOG_EXPORT_TITLE
        )

    def _confirm_renaming_if_exported_file_already_exists(self,name:str)->bool: # pragma: no cover
        return tkmsg.askokcancel(
            MSGBOX_ASK_TO_RENAME_TREE_TITLE,
            MSGBOX_ASK_TO_RENAME_TREE_MSG_1 + 
            name +
            MSGBOX_ASK_TO_RENAME_TREE_MSG_2
        )
    
    def _removal_confirmed(self,name:str)->bool:
        return tkmsg.askokcancel(   # pragma: no cover
            MSGBOX_ASK_TO_DELETE_TREE_TITLE, 
            MSGBOX_ASK_TO_DELETE_TREE_MSG_1 + 
            name + 
            MSGBOX_ASK_TO_DELETE_TREE_MSG_2
        )

    def _notify_tree_has_not_been_exported(self,name:str)->None:  # pragma: no cover
        tkmsg.showinfo(
            MSGBOX_TREE_WAS_NOT_YET_EXPORTED_TITLE,
            MSGBOX_TREE_WAS_NOT_YET_EXPORTED_MSG_1 + name +
            MSGBOX_TREE_WAS_NOT_YET_EXPORTED_MSG_2
        )
    
    def _error_if_tree_names_already_taken(self,name:str)->None:  # pragma: no cover
        tkmsg.showerror(
            NAME_ALREADY_TAKEN_TITLE, 
            NAME_ALREADY_TAKEN_MESSAGE_1+f"{name}"+NAME_ALREADY_TAKEN_MESSAGE_2
        )
                
    def _show_error_file_already_in_use(self,filepath:str,tree_name:str)->None:  # pragma: no cover
        tkmsg.showerror(MSGBOX_FILE_ALREADY_USED_TITLE, 
            MSGBOX_FILE_ALREADY_USED_MSG_1 + filepath + \
            MSGBOX_FILE_ALREADY_USED_MSG_2 + tree_name + \
            MSGBOX_FILE_ALREADY_USED_MSG_3
        )

    def _show_export_info(self,tree_name:str,filepath:str)->None: # pragma: no cover
        tkmsg.showinfo(INFO_TREE_EXPORTED_TITLE, 
            INFO_TREE_EXPORTED_MSG_1 + tree_name + \
            INFO_TREE_EXPORTED_MSG_2 + filepath + \
            INFO_TREE_EXPORTED_MSG_3
        )

    def _notify_the_user_selected_tree_cannot_be_deleted(self,tree_name:str)->None:
        tkmsg.showerror(SELECTED_TREE_CANNOT_BE_DELETED_TITLE, 
            SELECTED_TREE_CANNOT_BE_DELETED_MSG_1 + tree_name + \
            SELECTED_TREE_CANNOT_BE_DELETED_MSG_2
        )

    def __configure_ui(self)->None: # pragma: no cover
        button_frame = tk.Frame(self.__ui)
        self.__add_button(
            button_frame,
            ButtonID.NEW_TREE,
            command=self._open_new_tree_window,
            side='left'
        )
        self.__add_button(
            button_frame,
            ButtonID.LOAD_TREE,
            command=self._load_tree,
            side='left'
        )
        button_frame.pack(side=tk.BOTTOM)
        scroll_y = ttk.Scrollbar(self._view.master,orient=tk.VERTICAL,command=self._view.yview)
        scroll_y.pack(side=tk.LEFT,fill=tk.Y)

        self._view.config(
            selectmode='browse',
            show='tree', # hide zeroth row, that would contain the tree columns' headings
            yscrollcommand=scroll_y.set,
        )
        self._view.pack(side=tk.TOP,expand=1,fill=tk.BOTH)
        self.__ui.pack(expand=1,fill=tk.BOTH)

    def _bind_keys(self)->None:   # pragma: no cover
        self._view.bind("<Button-3>",self.right_click_item)
