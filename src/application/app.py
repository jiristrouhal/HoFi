from __future__ import annotations


from src.core.editor import blank_case_template, new_editor, Case_Template, Editor
from src.core.attributes import Locale_Code


from typing import Any, Dict, Literal


class App:

    __SettingLabel = Literal['currency']

    def __init__(
        self, 
        case_template:Case_Template=blank_case_template(), 
        locale_code:Locale_Code = "en_us"
        )->None:

        self.__locale_code = locale_code
        self.__editor = new_editor(case_template, locale_code)
        self.__settings:Dict[App.__SettingLabel,Any] = {
            'currency':"USD"
        }

    @property
    def locale_code(self)->str: return self.__locale_code
    @property
    def editor(self)->Editor: return self.__editor

    def settings(self, label:App.__SettingLabel)->Any: return self.__settings[label]

    def set(self, label:App.__SettingLabel, value:Any)->None:
        self.__settings[label] = value
    
