
import xml.etree.ElementTree as et
import os
from typing import Dict, Callable, List, Literal

import src.core.tree as treemod


class No_Template_For_Loaded_Element(Exception): 
    
    def __init__(self, message:str, unknown_tag:str)->None:
        super().__init__(message)
        self.unknown_tag = unknown_tag


DEFAULT_DIRECTORY = "."


def data_file_path(name:str,dir:str)->str:
    FORMAT = ".xml"
    if not os.path.isdir(dir): os.mkdir(dir)
    return os.path.join(dir,name+FORMAT)

class Tree_XML_Converter:
    __event_label = Literal['invalid_xml']
    def __init__(self, app_template:treemod.AppTemplate)->None:
        self._actions:Dict[str,List[Callable[[],None]]] = dict()
        self._app_template = app_template

    def actions(self,label:__event_label)->List[Callable[[],None]]:
        return self._actions[label]

    def add_action(self, label:__event_label, action:Callable[[],None])->None:
        if not label in self._actions: self._actions[label] = list()
        self._actions[label].append(action)

    def save_tree(self,tree:treemod.Tree,dir:str=DEFAULT_DIRECTORY)->str:
        xml_tree = self.__xml_tree(tree)
        
        path_to_file = data_file_path(tree.name, dir)
        if os.path.isfile(path_to_file): os.remove(path_to_file)

        et.indent(xml_tree,space="\t")
        xml_tree.write(path_to_file, encoding="UTF-8")

        return path_to_file

    def __xml_tree(self,tree:treemod.Tree)->et.ElementTree:
        attrib = {label:str(x.formatted_value) for label,x in tree.attributes.items()}
        xml_root = et.Element(tree.tag, attrib=attrib)
        self.__create_xml_elem(tree,xml_root)
        return et.ElementTree(xml_root)

    def __create_xml_elem(
        self,
        parent:treemod.TreeItem,
        parent_xml_elem:et.Element
        )->None:

        for branch in parent._children:
            attribs = {label:str(x.formatted_value) for label,x in branch.attributes.items()}
            xml_elem = et.SubElement(parent_xml_elem, branch.tag, attrib=attribs)
            self.__create_xml_elem(branch,xml_elem)

    def load_tree(self,name:str,dir:str=DEFAULT_DIRECTORY)->treemod.Tree|None:
        path_to_file = data_file_path(name,dir)
        if not os.path.isfile(path_to_file): 
            return None
    
        try: 
            xml_tree = et.parse(path_to_file)
        except:
            if 'invalid_xml' in self._actions:
                for action in self.actions('invalid_xml'):  action()
            return None

        xml_root = xml_tree.getroot()
        if xml_root.tag not in self._app_template.template_tags():
            raise No_Template_For_Loaded_Element(
                f"The xml element being loaded has tag {xml_root.tag}." 
                "The App_Template used for current application does not contain any template with this tag. "
                "The xml file is not compatible with the current version of the application. " 
                "Check the XML file, the language and version of the application.",
                xml_root.tag
            )

        tree = treemod.Tree(xml_root.attrib["name"],tag=xml_root.tag,app_template=self._app_template)
        for attr_name, value in xml_root.attrib.items():
            tree.set_attribute(attr_name,value)
        self.__load_xml_elem(xml_root,tree)
        return tree

    def __load_xml_elem(
        self,
        xml_elem:et.Element,
        thing_with_branches:treemod.TreeItem
        )->None:

        for elem in xml_elem:
            branch_name = elem.attrib["name"]
            if elem.tag not in self._app_template.template_tags():
                raise No_Template_For_Loaded_Element(
                    f"The loaded xml element (child of {xml_elem.tag}) has a tag {elem.tag}." 
                    "The App_Template used for current application does not contain any template with such a tag. "
                    "The xml file is not compatible with the current version of the application. "
                    "Check the XML file, the language and version of the application.",
                    elem.tag
                )
            thing_with_branches.new(branch_name,tag=elem.tag)
            child_branch = thing_with_branches._children[-1]
            
            for attr_name in child_branch._attributes:
                if attr_name in elem.attrib:
                    child_branch.set_attribute(attr_name, elem.attrib[attr_name])
            self.__load_xml_elem(elem,child_branch)
