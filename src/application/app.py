from __future__ import annotations


from src.core.editor import blank_case_template, new_editor, Case_Template, Editor
from src.core.attributes import Locale_Code


class App:
    def __init__(self, case_template:Case_Template=blank_case_template(), locale_code:Locale_Code = "en_us")->None:
        self.__locale_code = locale_code
        self.__editor = new_editor(case_template)

    @property
    def locale_code(self)->str: return self.__locale_code
    @property
    def editor(self)->Editor: return self.__editor