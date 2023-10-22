import tkinter as tk

from src.core.editor import EditorUI, Editor
from src.tkgui.item_actions import Item_Menu_Tk, Item_Window_Tk
from src.tkgui.caseview import Case_View_Tk

from typing import Tuple


class Editor_Tk(EditorUI):

    def __init__(
        self, 
        editor:Editor, 
        master_window:tk.Tk|tk.Frame, 
        displayable_attributes:Tuple[str,...]
        )->None:

        self.__win = master_window
        self.__item_window = Item_Window_Tk(self.__win)
        self.__item_menu = Item_Menu_Tk(self.__win)
        self.__caseview:Case_View_Tk = Case_View_Tk(self.__win, editor.root, *displayable_attributes)
        super().__init__(editor, self.__item_menu, self.__item_window, self.__caseview)

    def _compose(self) -> None:
        self.__caseview.widget.pack()
        self.__caseview.widget.bind(
            "<Button-3>",
            self.__caseview.do_on_tree_item(self.open_item_menu)
        )
        self.__caseview.widget.bind(
            "<Double-Button-1>",
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
