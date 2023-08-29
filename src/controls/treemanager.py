
from typing import List, Dict, Callable, Any, Literal
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tkmsg
import tkinter.filedialog as filedialog
from functools import partial
import os
import sys

sys.path.insert(1,"src")


import src.controls.tree_to_xml as txml
import src.controls.treelist as treelist
import src.core.tree as treemod
import src.controls.right_click_menu as rcm
import src.lang.lang as lang


class Tree_Manager:

    def __init__(
        self,
        treelist:treelist.TreeList,
        app_template:treemod.AppTemplate,
        tree_tag:str,
        ui_master:tk.Frame|tk.Tk|tk.LabelFrame|None = None,
        label:str = "Manager"
        )->None:

        if not tree_tag in app_template.template_tags():
            raise KeyError(f"The tree template '{tree_tag} does not exist.")
        self._tree_template_tag:str = tree_tag
        self._app_template = app_template

        voc = lang.Vocabulary()
        voc.load_xml(os.path.join(os.path.dirname(__file__), 'loc'), app_template.locale_code)
        self.vocabulary = voc.subvocabulary("Manager")

        self.name_attr = app_template.name_attr
        self.__label = label
        self._converter = txml.Tree_XML_Converter(app_template)
        self._converter.add_action('invalid_xml', self._notify_the_user_xml_is_invalid)
        self.__ui = tk.Frame(master=ui_master)
        self._view = ttk.Treeview(self.__ui, selectmode='browse', columns=('State',))
        self._map:Dict[str,treemod.Tree] = dict()

        self._window_new = tk.Toplevel(self._view)
        self._window_new.wm_withdraw()
        self.entries:Dict[str,tk.Entry] = dict()
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
    def label(self)->str: return self.__label
    @property
    def trees(self)->List[str]: return self.__treelist.names
    @property
    def unsaved_trees(self)->bool: return bool(self.__treelist._modified_trees)

    def add_action_on_selection(self,action:Callable[[treemod.Tree],None])->None:
        if action not in self.__on_selection:
            self.__on_selection.append(action)

    def add_action_on_deselection(self,action:Callable[[treemod.Tree],None])->None:
        if action not in self.__on_deselection:
            self.__on_deselection.append(action)

    def new(
        self,
        name:str
        )->None: 

        tree = treemod.Tree(
            name, 
            tag=self._tree_template_tag, 
            app_template=self._app_template
        )

        self.__treelist.append(tree)
        tree.add_data("treemanager_id",str(id(tree)))
        self.label_tree_as_waiting_for_export(tree)

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
                self.vocabulary("Right_Click_Menu","New") : self._open_new_tree_window,
                self.vocabulary("Right_Click_Menu","Load"): self._load_tree
            }
        )

    def _open_right_click_menu_for_item(self,item_id:str)->None:
        labels = self.vocabulary.subvocabulary("Right_Click_Menu")
        self.right_click_menu = rcm.RCMenu(master=self._view, tearoff=False)
        tree = self._map[item_id]
        if tree in self._selected_trees:
            self.right_click_menu.add_single_command(
                labels("Stop_Editing"), partial(self._deselect,item_id)
            )
        else:
            self.right_click_menu.add_single_command(
                labels("Edit"), partial(self._select,item_id)
            )
        self.right_click_menu.add_separator()
        self.right_click_menu.add_single_command(
            labels("Rename"),partial(self._open_rename_tree_window,tree)
        )
        if tree in self._tree_files:
            self.right_click_menu.add_single_command(
                labels("Update_File"), partial(self._update_file,tree)
            )

        self.right_click_menu.add_single_command(
            labels("Export"),partial(self._export_tree,tree)
        )
        self.right_click_menu.add_separator()
        self.right_click_menu.add_single_command(
            labels("Delete"), partial(self._remove_tree,tree)
        )

    def _get_filepath(self)->str:
        return filedialog.askopenfilename(   # pragma: no cover
            title=self.vocabulary("Load_From_File"),
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
        if self.tree_exists(treename): 
            self._cannot_load_tree_with_already_taken_name(treename)
            return
        if self.__file_already_in_use(filepath): 
            return 
        
        try:
            tree = self._converter.load_tree(treename,dir)
        except txml.No_Template_For_Loaded_Element as e:
            self._notify_the_user_of_missing_template(e.unknown_tag)
            return

        if tree is None: return

        self._tree_files[tree] = filepath
        self.__treelist.append(tree)
        tree.add_data("treemanager_id",str(id(tree)))
        self.label_tree_as_ok(tree)

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
            filepath = self._converter.save_tree(tree,dir)
            self._show_export_info(tree.name,filepath)
            self._tree_files[tree] = os.path.join(dir,tree.name)+'.xml'
            self._last_export_dir = dir
            self.label_tree_as_ok(tree)

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
        new_filepath = self._converter.save_tree(tree,dir)
        self._tree_files[tree] = new_filepath
        self.label_tree_as_ok(tree)

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
        label:str,
        command:Callable[[],None], 
        side:Literal['left','right','top','bottom']
        )->None:
        
        tk.Button(master,text=label,command=command).pack(side=side)

    def _open_rename_tree_window(self,tree:treemod.Tree)->None: # pragma: no cover
        labels = self.vocabulary.subvocabulary("Rename_Window")
        self.__cleanup_rename_tree_widgets()
        self._window_rename = tk.Toplevel(self.__ui)
        self._window_rename.title(labels("Title"))
        self._entry_name = tk.Entry(self._window_rename,width=50)
        self._entry_name.pack()
        self._entry_name.insert(0,tree.name)

        button_frame = tk.Frame(self._window_rename)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(
            button_frame,
            labels("OK_Button"),
            partial(self._confirm_rename,tree),
            side='left'
        )
        self.__add_button(
            button_frame,
            labels("Cancel_Button"),
            self._close_rename_tree_window,
            side='left'
        )
        
    def __create_entries(
        self,window:tk.Toplevel,
        attributes:Dict[str,treemod._Attribute],
        excluded:List[str]=[]
        )->None:  
        
        entries_frame = tk.Frame(window)
        row=0
        for key,attr in attributes.items():
            if key in excluded: continue
            col=0
            tk.Label(entries_frame,text=key).grid(row=row,column=col)
            col += 1
            if attr.options:
                box = ttk.Combobox(entries_frame,values=attr.options)
                box.insert(0, attr.formatted_value)
                box.current(attr.options.index(attr.formatted_value))
                box.grid(row=row,column=col)
                self.entries[key] = box
            else:
                vcmd = (entries_frame.register(attr.valid_entry),'%P')
                entry = tk.Entry(entries_frame, validate='key', validatecommand=vcmd)
                entry.insert(0, attr.value)
                entry.grid(row=row,column=col)
                self.entries[key] = entry
            row += 1
        entries_frame.pack()

    def _open_new_tree_window(self)->None: # pragma: no cover
        self.__cleanup_new_tree_widgets()
        self._window_new = tk.Toplevel(self.__ui)
        self._window_new.title(self.vocabulary("New_Tree_Window","Title")+' '+self._tree_template_tag)
        self.__create_entries(
            self._window_new, 
            self._app_template(self._tree_template_tag).attributes
        )
        
        button_frame = tk.Frame(self._window_new)
        button_frame.pack(side=tk.BOTTOM)
        self.__add_button(
            button_frame,
            self.vocabulary("New_Tree_Window","OK_Button"),
            self._confirm_new_tree,
            side='left'
        )
        self.__add_button(
            button_frame,
            self.vocabulary("New_Tree_Window","Cancel_Button"),
            self.__close_new_tree_window,
            side='left'
        )

    def _confirm_rename(self,tree:treemod.Tree)->None:
        new_name = self._entry_name.get()
        if self.tree_exists(new_name) and self.get_tree(new_name) is not tree: 
            self._error_if_tree_names_already_taken(new_name)
        else:
            self.rename(tree.name,self._entry_name.get())
            self._close_rename_tree_window()

    def _confirm_new_tree(self)->None:
        attributes = self._app_template(self._tree_template_tag).attributes
        for label, entry in self.entries.items():
            attributes[label].set(entry.get())
        name = attributes.pop(self.name_attr).value
        self.new(name)
        new_tree = self.__treelist._items[-1]
        for attr_name in attributes:
            new_tree.set_attribute(attr_name,attributes[attr_name].value)
        self.__close_new_tree_window()

    def _close_rename_tree_window(self)->None:
        self.__cleanup_rename_tree_widgets()

    def __close_new_tree_window(self)->None:
        self.__cleanup_new_tree_widgets()

    def __cleanup_new_tree_widgets(self)->None:
        self._window_new.destroy()
        self._entry_name.destroy()
        for item in self.entries.values():
            item.destroy()
        self.entries.clear()

    def __cleanup_rename_tree_widgets(self)->None:
        self._window_rename.destroy()
        self._entry_name.destroy()
        for item in self.entries.values():
            item.destroy()
        self.entries.clear()

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

    def _set_tree_attribute(self,name:str,key:str,value:Any)->None:
        tree = self.get_tree(name)
        if tree is None: return
        if key in tree.attributes:
            if key==self.name_attr: self.__treelist.rename(tree.name, value)
            else: tree._attributes[key].set(value)

    def rename(self,old_name:str,new_name:str)->None:
        renamed_tree = self.__treelist.rename(old_name,new_name)
        if renamed_tree is None:
            # renaming of a nonexistent tree has been attempted, no further action is taken
            return 

        # After renaming, the file associated with the tree cannot be simply updated
        # and the tree is to be exported anew.
        # This helps to prevent unwanted rewriting of some existing file having
        # the same name as the newly named Tree that is to be updated
        if old_name.strip() != new_name.strip():
            self.label_tree_as_waiting_for_export(renamed_tree)
            if renamed_tree in self._tree_files: 
                self._tree_files.pop(renamed_tree)

    def tree_exists(self,name:str)->bool: 
        return name in self.trees
    

    def _ask_for_directory(self)->str:  # pragma: no cover
        return filedialog.askdirectory(
                initialdir=self._last_export_dir,
                title = self.vocabulary("Export_File_Dialog_Title")
        )

    def _confirm_renaming_if_exported_file_already_exists(self,name:str)->bool: # pragma: no cover
        msg_labels = self.vocabulary.subvocabulary("Confirm_Renaming_If_Exported_File_Exists")
        return tkmsg.askokcancel(
            msg_labels("Title"),
            name + ": "+msg_labels("Message")
        )
    
    def _removal_confirmed(self,name:str)->bool:
        msg_labels = self.vocabulary.subvocabulary("Confirm_Removal")
        return tkmsg.askokcancel(
            msg_labels("Title"),
            name + ": "+msg_labels("Message")
        )

    def _notify_tree_has_not_been_exported(self,name:str)->None:  # pragma: no cover
        msg_labels = self.vocabulary.subvocabulary("Not_Yet_Exported")
        tkmsg.showinfo(msg_labels("Title"), name+": "+msg_labels("Message"))
    
    def _error_if_tree_names_already_taken(self,name:str)->None:  # pragma: no cover
        tkmsg.showerror(
            self.vocabulary("Error_Name_Already_Taken","Title"), 
            name+self.vocabulary("Error_Name_Already_Taken","Content")
        )

    def _cannot_load_tree_with_already_taken_name(self,name:str)->None:  # pragma: no cover
        msg_labels = self.vocabulary.subvocabulary("Cannot_Load_If_Name_Already_Taken")
        tkmsg.showerror(msg_labels("Title"), name+": "+msg_labels("Message"))
                
    def _show_error_file_already_in_use(self,filepath:str,tree_name:str)->None:  # pragma: no cover
        msg_labels = self.vocabulary.subvocabulary("File_Already_In_Use")
        tkmsg.showerror(msg_labels("Title"), 
            msg_labels("Message_part_1") + filepath + \
            msg_labels("Message_part_2") + tree_name + \
            msg_labels("Message_part_3")
        )

    def _show_export_info(self,tree_name:str,filepath:str)->None: # pragma: no cover
        msg_labels = self.vocabulary.subvocabulary("Export_Info")
        tkmsg.showinfo(msg_labels("Title"), 
            msg_labels("Message_part_1") + tree_name + \
            msg_labels("Message_part_2") + filepath + \
            msg_labels("Message_part_3")
        )

    def _notify_the_user_selected_tree_cannot_be_deleted(self,tree_name:str)->None:
        msg_labels = self.vocabulary.subvocabulary("Cannot_Be_Deleted")
        tkmsg.showerror(
            msg_labels("Title"), 
            tree_name + ": " + msg_labels("Message")
        )

    def _notify_the_user_xml_is_invalid(self)->None:
        msg = self.vocabulary.subvocabulary("Invalid_XML")
        tkmsg.showerror(msg("Title"), msg("Content"))

    def _notify_the_user_of_missing_template(self, missing_elem_tag:str)->None:
        msg = self.vocabulary.subvocabulary("Missing_Template_For_XML_Elem")
        tkmsg.showerror(
            msg("Title"), 
            msg("Message_part_1") + missing_elem_tag + msg("Message_part_2"))
                        
    def label_tree_as_modified(self,tree:treemod.TreeItem)->None:
        if not tree in self.__treelist._modified_trees:
            self._view.item(
                tree.data["treemanager_id"], 
                values=(self.vocabulary("Tree_Status_Labels","Modified"),)
            )
            self.__treelist.add_tree_to_modified(tree)

    def label_tree_as_ok(self,tree:treemod.TreeItem)->None:
        self._view.item(
            tree.data["treemanager_id"], 
            values=(self.vocabulary("Tree_Status_Labels","OK"),)
        )
        if tree in self.__treelist._modified_trees:
            self.__treelist._modified_trees.remove(tree)
    
    def label_tree_as_waiting_for_export(self,tree:treemod.TreeItem)->None:
        self._view.item(
            tree.data["treemanager_id"], 
            values=(self.vocabulary("Tree_Status_Labels","Waiting_For_Export"),)
        )
        self.__treelist.add_tree_to_modified(tree)

    def label_items_tree_as_modified(self,item:treemod.TreeItem)->None:
        tree = item.its_tree
        if not tree in self.__treelist._modified_trees:
            self.label_tree_as_modified(tree)
            self.__treelist.add_tree_to_modified(tree)

    def __configure_ui(self)->None: # pragma: no cover
        button_frame = tk.Frame(self.__ui)
        self.__add_button(
            button_frame,
            self.vocabulary("Buttons","New"),
            command=self._open_new_tree_window,
            side='left'
        )
        self.__add_button(
            button_frame,
            self.vocabulary("Buttons","Load"),
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
