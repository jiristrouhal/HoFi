import tree
from typing import List, Dict


class App:

    def __init__(self)->None:
        self._trees:Dict[str,tree.Tree] = dict()
    
    @property
    def trees(self)->List[str]: return [t for t in self._trees.keys()]

    def new_tree(self,name:str)->None: 
        if name in self._trees: # do not create new tree, if the tree name is already taken
            return
        self._trees[name] = tree.Tree()

    def remove_tree(self,name:str)->None: 
        self._trees.pop(name)

    def rename_tree(self,old_name:str,new_name:str)->None:
        if old_name!=new_name and new_name in self._trees: 
            # tree cannot be renamed, if the new name is taken by other tree
            return
        self._trees[new_name] = self._trees.pop(old_name)