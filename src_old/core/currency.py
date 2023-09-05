from typing import Dict, Literal, Tuple
from src.lang.lang import Locale_Code
from decimal import Decimal, Context
import decimal
import re
import dataclasses


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


LOCALIZATION_CODE = 'en_us'
DEFAULT_CURRENCY_CODE = CURRY_CODE_BY_LOCALIZATION[LOCALIZATION_CODE]


def set_localization(code:Locale_Code)->None:
    global LOCALIZATION_CODE, DEFAULT_CURRENCY_CODE
    LOCALIZATION_CODE = code
    DEFAULT_CURRENCY_CODE = CURRY_CODE_BY_LOCALIZATION[LOCALIZATION_CODE]




@dataclasses.dataclass
class __Curry_Format:
    decimals:Literal[0,1,2,3]
    symbol:str
    prepend:bool = True
    def __post_init__(self):
        if self.decimals>0:
            self.context = Context(prec=self.decimals,rounding=decimal.ROUND_HALF_EVEN)

    def present(self,value:Decimal|float|str,locale_code:Locale_Code)->str:
        value = str(value).replace(",",".")
        if self.decimals==0:
            value = int(value)
        else:
            value =  round(Decimal(str(value),self.context), self.decimals)
        if CURRY_SYMBOL_POSITION[locale_code]==0 and self.prepend:
            return self.__prepend_symbol(value)
        else:
            return self.__append_symbol(value)

    def __prepend_symbol(self,value:Decimal|float|str)->str:
        return self.symbol+str(value)

    def __append_symbol(self,value:Decimal|float|str)->str:
        return str(value) + ' ' + self.symbol
        


class UndefinedCurrency(Exception): pass


CURRY_FORMATS:Dict[Currency_Code,__Curry_Format] = {
    'CZK':__Curry_Format(2,'Kč',prepend=False),
    'EUR':__Curry_Format(2,'€'),
    'USD': __Curry_Format(2,'$'),
    'JPY': __Curry_Format(0,'¥')
}
CURRY_CODES = [code for code in CURRY_FORMATS]
CURRENCY_SYMBOLS = [CURRY_FORMATS[code].symbol for code in CURRY_FORMATS]
CURR_SYMBOLS_TO_CODE = {CURRY_FORMATS[code].symbol:code for code in CURRY_FORMATS}


def convert_to_currency(text:str)->Tuple[Decimal,str]|Tuple:
    text = str(text).strip().replace(",",".")
    if re.fullmatch("\d+(\.\d*)?\s*\S*",text) is not None or re.fullmatch("\.\d+\s*\S*",text) is not None:
        i = 0
        while i<len(text) and (text[i].isdigit() or text[i]=='.'):  
            i += 1
        text_without_number = text[i:].strip()
        if text_without_number in CURRENCY_SYMBOLS:
            currency_code = CURR_SYMBOLS_TO_CODE[text_without_number]
            return (Decimal(text[:i]), currency_code)
        return ()
    
    elif re.fullmatch("\S*\s*\d+(\.\d*)?",text) is not None:
        i = -1
        while  i>-len(text)-1 and (text[i].isdigit() or text[i]=='.'):
            i -= 1
        text_without_number = text[:i+1].strip()
        if text_without_number in CURRENCY_SYMBOLS:
            currency_code = CURR_SYMBOLS_TO_CODE[text_without_number]
            return (Decimal(text[i+1:]), currency_code)
        return ()
    
    return ()
