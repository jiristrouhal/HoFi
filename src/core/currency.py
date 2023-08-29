from typing import Dict, Literal
from src.lang.lang import Locale_Code


Curry_Symbol_Position = Literal[0,1]
Currency_Code = Literal['CZK','EUR', 'USD','JPY']


CURRY_SYMBOL_POSITION:Dict[Locale_Code, Curry_Symbol_Position] = {
    'en_us':0,
    'cs_cz':1
}

CURRY_CODE_BY_LOCALIZATION:Dict[Locale_Code, Currency_Code] = {
    'en_us': 'USD',
    'cs_cz': 'CZK'
}