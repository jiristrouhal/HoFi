import tree
from typing import List, Dict


class App:

    def __init__(self)->None:
        self._trees:Dict[str,tree.Tree] = dict()
    
    @property
    def trees(self)->List[str]: return [t for t in self._trees.keys()]

    def new_tree(self,name:str)->None: 
        self._trees[name] = tree.Tree()

    def remove_tree(self,name:str)->None: 
        self._trees.pop(name)