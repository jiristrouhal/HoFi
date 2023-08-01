import tkinter
from tkinter.ttk import Treeview
import xml.etree.ElementTree as et


def read_tree_data(path:str)->et.ElementTree:
    return et.parse(path)


