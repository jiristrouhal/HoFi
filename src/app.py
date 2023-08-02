import tree
from typing import List, Dict
import xml.etree.ElementTree as et
import os


FILES_PATH = "./data"

def data_file_path(name:str)->str:
    FORMAT = ".xml"
    if not os.path.isdir(FILES_PATH): os.mkdir(FILES_PATH)
    return os.path.join(FILES_PATH,name+FORMAT)

class App:

    def __init__(self)->None:
        self._trees:Dict[str,tree.Tree] = dict()
    
    @property
    def trees(self)->List[str]: return [t for t in self._trees.keys()]

    def tree(self,name:str)->tree.Tree:
        if name in self._trees: return self._trees[name]

    def new_tree(self,name:str)->None: 
        if name in self._trees: # do not create new tree, if the tree name is already taken
            return
        self._trees[name] = tree.Tree()

    def remove_tree(self,name:str)->None: 
        if name not in self._trees: return
        self._trees.pop(name)

    def rename_tree(self,old_name:str,new_name:str)->None:
        if old_name not in self._trees: return
        if old_name!=new_name and new_name in self._trees: 
            # tree cannot be renamed, if the new name is taken by other tree
            return
        self._trees[new_name] = self._trees.pop(old_name)

    def save_new_tree(self,name:str)->None:
        if name not in self._trees: return
        
        path_to_file = data_file_path(name)
        if os.path.isfile(path_to_file): os.remove(path_to_file)

        root = et.Element("Tree",{"name":name})
        et.ElementTree(root).write(path_to_file)

    def load_tree(self,name:str)->None:
        path_to_file = data_file_path(name)
        if not os.path.isfile(path_to_file): return
        xml = et.parse(path_to_file)
        root = xml.getroot()
        if root is not None:
            self.new_tree(root.attrib["name"])
