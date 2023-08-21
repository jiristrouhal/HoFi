
import xml.etree.ElementTree as et
import os
from collections import OrderedDict

import src.core.tree as treemod


DEFAULT_DIRECTORY = "./data"


def data_file_path(name:str,dir:str)->str:
    FORMAT = ".xml"
    if not os.path.isdir(dir): os.mkdir(dir)
    return os.path.join(dir,name+FORMAT)

class Tree_XML_Converter:

    def save_tree(self,tree:treemod.Tree,dir:str=DEFAULT_DIRECTORY)->str:
        xml_tree = self.__xml_tree(tree)
        
        path_to_file = data_file_path(tree.name, dir)
        if os.path.isfile(path_to_file): os.remove(path_to_file)

        et.indent(xml_tree,space="\t")
        xml_tree.write(path_to_file, encoding="UTF-8")

        return path_to_file

    def __xml_tree(self,tree:treemod.Tree)->et.ElementTree:
        attrib = {label:str(x.value) for label,x in tree.attributes.items()}
        xml_root = et.Element(tree.tag, attrib=attrib)
        self.__create_xml_elem(tree,xml_root)
        return et.ElementTree(xml_root)

    def __create_xml_elem(
        self,
        parent:treemod.TreeItem,
        parent_xml_elem:et.Element
        )->None:

        for branch in parent._children:
            attribs = {label:str(x.value) for label,x in branch.attributes.items()}
            xml_elem = et.SubElement(parent_xml_elem, branch.tag, attrib=attribs)
            self.__create_xml_elem(branch,xml_elem)

    def load_tree(self,name:str,dir:str=DEFAULT_DIRECTORY)->treemod.Tree|None:
        path_to_file = data_file_path(name,dir)
        if not os.path.isfile(path_to_file): return None
        
        xml_root = et.parse(path_to_file).getroot()
        tree = treemod.Tree(xml_root.attrib["name"],tag=xml_root.tag)
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
            thing_with_branches.new(branch_name,tag=elem.tag)
            child_branch = thing_with_branches._find_child(branch_name)
            if child_branch is None: return 

            for attr_name in child_branch.attributes:
                if attr_name in elem.attrib:
                    child_branch.set_attribute(attr_name, elem.attrib[attr_name])
            self.__load_xml_elem(elem,child_branch)
