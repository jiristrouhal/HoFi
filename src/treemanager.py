import tree_to_xml as txml
from typing import List
import naming


class Tree_Manager:

    def __init__(self)->None:
        self.__converter = txml.Tree_XML_Converter()

    @property
    def trees(self)->List[str]: return self.__converter.trees

    def new(self,name:str)->None: 
        while self.__tree_name_is_taken(name):
            name = naming.change_name_if_already_taken(name)
        self.__converter.new_tree(name)

    def __tree_name_is_taken(self,name:str)->bool: return name in self.trees
    