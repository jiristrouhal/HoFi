import tree as tree_module
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
        self._trees:Dict[str,tree_module.Tree] = dict()
    
    @property
    def trees(self)->List[str]: return [t for t in self._trees.keys()]

    def tree(self,name:str)->tree_module.Tree:
        if name in self._trees: return self._trees[name]

    def new_tree(self,name:str)->None: 
        if name in self._trees: # do not create new tree, if the tree name is already taken
            return
        self._trees[name] = tree_module.Tree()

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
        xml_tree = self.__xml_tree(name)
        if xml_tree is None: return
        
        path_to_file = data_file_path(name)
        if os.path.isfile(path_to_file): 
            os.remove(path_to_file)

        et.indent(xml_tree,space="\t")
        xml_tree.write(path_to_file)

    def __xml_tree(self,name:str)->et.ElementTree|None:
        tree = self.tree(name)
        if tree is None: return None

        xml_root = et.Element("Tree", {"name":name})
        self.__create_xml_elem(tree,xml_root)
        return et.ElementTree(xml_root)

    def __create_xml_elem(
        self,
        parent:tree_module.TreeItem,
        parent_xml_elem:et.Element
        )->None:

        for branch in parent._branches:
            xml_elem = et.SubElement(parent_xml_elem,"Branch",branch.attributes)
            self.__create_xml_elem(branch,xml_elem)

    def load_tree(self,name:str)->None:
        path_to_file = data_file_path(name)
        if not os.path.isfile(path_to_file): return

        xml = et.parse(path_to_file)
        xml_root = xml.getroot()
        if xml_root is None: return
        
        self.new_tree(xml_root.attrib["name"])
        tree = self.tree(xml_root.attrib["name"])
        self.__load_xml_elem(xml_root,tree)

    def __load_xml_elem(
        self,
        xml_elem:et.Element,
        thing_with_branches:tree_module.TreeItem
        )->None:

        for elem in xml_elem.findall("Branch"):
            branch_name = elem.attrib["name"]
            thing_with_branches.add_branch(branch_name,attributes=elem.attrib)

            child_branch = thing_with_branches._find_branch(branch_name)
            self.__load_xml_elem(elem,child_branch)
