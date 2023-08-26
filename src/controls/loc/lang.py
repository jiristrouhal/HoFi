

from typing import Literal, Dict, Tuple, Callable
from functools import partial
import xml.etree.ElementTree as et
import dataclasses


LANG_XML_PATH_RELATIVE_TO_PROJECT_FOLDER = "src/controls/loc/"


_Language_Code = Literal['en_us','cs_cz']
@dataclasses.dataclass
class Vocabulary:
    language_code:_Language_Code
    vocabulary:Dict[Tuple[str,...],str] = dataclasses.field(default_factory=dict, init=False)
    _language:et.Element = dataclasses.field(init=False)

    def __post_init__(self)->None:
        self._language = et.parse(LANG_XML_PATH_RELATIVE_TO_PROJECT_FOLDER+self.language_code+".xml").getroot()

    def subvocabulary(self,*xml_elem_path:str)->Callable[[str],str]:
        # validate the entered path
        assert (self._language is not None)
        parent = self._language
        for elem in xml_elem_path[:-1]:
            assert(parent is not None)
            next_item = parent.find(elem)
            if next_item is None: raise ValueError
            else: parent = next_item
        return partial(self.text,*xml_elem_path)
    
    def text(self,*xml_tree_path:str)->str:
        if xml_tree_path not in self.vocabulary:
            self.__find_new_text_and_add_to_vocabulary(*xml_tree_path)
        return self.vocabulary[xml_tree_path]
    
    def __find_new_text_and_add_to_vocabulary(self,*xml_tree_path:str)->None:
        assert (self._language is not None)
        parent = self._language

        for elem in xml_tree_path[:-1]:
            assert(parent is not None)
            next_item = parent.find(elem)
            if next_item is None: raise ValueError
            else: parent = next_item

        text_item = parent.find(xml_tree_path[-1])
        if text_item is None: raise ValueError
        else: self.vocabulary[xml_tree_path] = text_item.attrib["Text"]