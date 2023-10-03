from typing import Optional, List, Tuple


class Case_Template:

    def __init__(self) -> None:
        self.__templates:List[str] = list()

    @property
    def templates(self)->Tuple[str,...]: return tuple(self.__templates)

    def add_template(self, label:str)->None:
        if label in self.__templates: raise Case_Template.TemplateAlreadyDefined(label)
        self.__templates.append(label)

    class TemplateAlreadyDefined(Exception): pass


class Case:

    def __init__(self,name:str)->None:
        self.__name = name

    @property
    def name(self)->str: return self.__name


class Editor:

    def __init__(self)->None:
        self.__case_template:Optional[Case_Template] = None

    def set_case_template(self, case_template:Case_Template)->None:
        self.__case_template = case_template

    def new_case(self, name:str)->Case:
        if self.__case_template is None: raise Editor.CaseTemplateNotSet
        return Case(name)
    
    class CaseTemplateNotSet(Exception): pass


def new_case_template()->Case_Template:
    return Case_Template()


def new_editor()->Editor:
    return Editor()