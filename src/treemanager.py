import tree_to_xml as txml
from typing import List


class Tree_Manager:

    def __init__(self)->None:
        self.__converter = txml.Tree_XML_Converter()

    @property
    def trees(self)->List[str]: return self.__converter.trees

    def new(self,name:str)->None: self.__converter.new_tree(name)
    