import tkinter
import xml.etree.ElementTree as et


def read_tree(path:str)->et.ElementTree:
    return et.parse(path)


