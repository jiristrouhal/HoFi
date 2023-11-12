import tkinter as tk

from src.core.editor import EditorUI, Editor, Lang_Object
from src.tkgui.item_actions import Item_Menu_Tk, Item_Window_Tk
from src.tkgui.caseview import Case_View_Tk

from typing import Tuple, Dict
from tkinter.filedialog import askopenfilename, askdirectory
import os

class Editor_Tk(EditorUI):

    def __init__(
        self, 
        editor:Editor, 
        master_window:tk.Tk|tk.Frame, 
        displayable_attributes:Dict[str,Tuple[str,...]],
        lang:Lang_Object
        )->None:

        self.__win = master_window
        self.__item_window = Item_Window_Tk(self.__win)
        self.__item_menu = Item_Menu_Tk(self.__win, lang=lang)
        self.__caseview:Case_View_Tk = Case_View_Tk(self.__win, editor.root, displayable_attributes)
        super().__init__(editor, self.__item_menu, self.__item_window, self.__caseview, lang=lang)

    def _compose(self) -> None:
        self.__caseview.widget.pack()
        self.__caseview.widget.bind(
            "<Button-3>",
            self.__caseview.do_on_tree_item(self.open_item_menu)
        )
        self.__caseview.widget.bind(
            "<Return>",
            self.__caseview.do_on_tree_item(self.open_item_window)
        )
        self.__caseview.widget.bind(
            "<Control-z>",
            lambda e: self.editor.undo()
        )
        self.__caseview.widget.bind(
            "<Control-y>",
            lambda e: self.editor.redo()
        )
        self.__caseview.widget.bind(
            "<Delete>",
            self.__caseview.do_on_tree_item(self.delete_item)
        )

    def _get_xml_path(self) -> Tuple[str, str]:
        case_full_path = askopenfilename(defaultextension="xml", filetypes=[("xml","xml")])
        if case_full_path is None: 
            return "",""
        else:
            return os.path.dirname(case_full_path), os.path.basename(case_full_path).split(".")[0]
        
    def _get_export_dir(self) -> str:
        return askdirectory(initialdir=self.editor.export_dir_path)