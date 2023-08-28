

from __future__ import annotations
from typing import Literal, Dict, Tuple
import xml.etree.ElementTree as et
import dataclasses
import os


class UninitiallizedVocabulary(Exception): pass


_Language_Code = Literal['en_us','cs_cz']
@dataclasses.dataclass
class Vocabulary:
    vocabulary:Dict[Tuple[str,...],str] = dataclasses.field(default_factory=dict, init=False)
    _xml_root:et.Element|None = None

    def load_xml(self,folder:str,language_code:_Language_Code)->None:
        self.vocabulary.clear()
        path = os.path.join(os.path.dirname(__file__),folder,(language_code+".xml")).replace("\\","/")
        try:
            self._xml_root = et.parse(path).getroot()
        except:
            raise ValueError(f"Cannot find file for localization code {language_code} "
                             f"on path {os.path.dirname(path)}.")

    def set_data(self,data:et.Element)->None:
        self._xml_root = data
    
    def __call__(self,*xml_tree_path:str)->str:
        return self.text(*xml_tree_path)

    def subvocabulary(self,*xml_elem_path:str)->Vocabulary:
        subvoc = Vocabulary()
        subvoc.set_data(self.__find_xml_elem(*xml_elem_path))
        return subvoc
    
    def text(self,*xml_tree_path:str)->str:
        if xml_tree_path not in self.vocabulary:
            self.__find_new_text_and_add_to_vocabulary(*xml_tree_path)
        return self.vocabulary[xml_tree_path]
    
    def __find_new_text_and_add_to_vocabulary(self,*xml_tree_path:str)->None:
        elem = self.__find_xml_elem(*xml_tree_path)
        self.vocabulary[xml_tree_path] = elem.attrib["Text"]
    
    def __find_xml_elem(self,*elem_path:str):
        if self._xml_root is None:
            raise UninitiallizedVocabulary("The vocabulary xml source was not propertly loaded. Use 'load_xml' method.")
        parent = self._xml_root
        for elem in elem_path:
            next_item = parent.find(elem)
            if next_item is None: 
                raise ValueError(f"The xml element '{parent}' does not containg element '{elem}'.\n"
                                 f"Available elements are {parent}")
            else: parent = next_item
        return parent
