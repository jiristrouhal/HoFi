import tree as treemod
import xml.etree.ElementTree as et
import os


DEFAULT_DIRECTORY = "./data"


def data_file_path(name:str,dir:str)->str:
    FORMAT = ".xml"
    if not os.path.isdir(dir): os.mkdir(dir)
    return os.path.join(dir,name+FORMAT)

class Tree_XML_Converter:

    def save_tree(self,tree:treemod.Tree,dir:str=DEFAULT_DIRECTORY)->None:
        xml_tree = self.__xml_tree(tree)
        
        path_to_file = data_file_path(tree.name, dir)
        if os.path.isfile(path_to_file): os.remove(path_to_file)

        et.indent(xml_tree,space="\t")
        xml_tree.write(path_to_file)

    def __xml_tree(self,tree:treemod.Tree)->et.ElementTree:
        xml_root = et.Element(tree.tag, {"name":tree.name})
        self.__create_xml_elem(tree,xml_root)
        return et.ElementTree(xml_root)

    def __create_xml_elem(
        self,
        parent:treemod.TreeItem,
        parent_xml_elem:et.Element
        )->None:

        for branch in parent._children:
            xml_elem = et.SubElement(parent_xml_elem,branch.tag,branch.attributes)
            self.__create_xml_elem(branch,xml_elem)

    def load_tree(self,name:str,dir:str=DEFAULT_DIRECTORY)->treemod.Tree|None:
        path_to_file = data_file_path(name,dir)
        if not os.path.isfile(path_to_file): return None

        xml = et.parse(path_to_file)
        xml_root = xml.getroot()
        
        tree = treemod.Tree(xml_root.attrib["name"])
        self.__load_xml_elem(xml_root,tree)
        return tree

    def __load_xml_elem(
        self,
        xml_elem:et.Element,
        thing_with_branches:treemod.TreeItem
        )->None:

        for elem in xml_elem:
            branch_name = elem.attrib["name"]
            thing_with_branches.add_branch(branch_name,attributes=elem.attrib)

            child_branch = thing_with_branches._find_branch(branch_name)
            self.__load_xml_elem(elem,child_branch)
