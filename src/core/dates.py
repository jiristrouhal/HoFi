import datetime
from typing import Dict


from src.lang.lang import Locale_Code


SEPARATORS = (".","_","-"," ")

class Date_Converter:

    def __init__(self,user_format:str)->None:
        self.__format = user_format

    def enter_date(self,readable_date:str)->datetime.date|None:
        return datetime.datetime.strptime(readable_date, self.__format)

    def validate_date(self,readable_date:str)->bool:
        try: 
            datetime.datetime.strptime(readable_date, self.__format)
            return True
        except: 
            return False

    def print_date(self,date_obj:datetime.date)->str:
        return Date_Converter.__date_to_str(date_obj, self.__format)
    
    def set(self,new_format_string:str)->None:
        self._validate_format(new_format_string)
        self.__format = new_format_string

    @staticmethod
    def _validate_format(format:str)->None:
        elems = ('%d','%m','%Y')
        for c in ('%d','%m','%Y'):
            if not format.count(c)==1:
                raise ValueError(f"The date format must contain {c} exactly once.")


        if not format[:2] in elems: 
            raise ValueError(f"'{format[:2]}' cannot be on the beginning of the date format string."\
                            " Use '%d', '%m' or '%Y'.")
        
        if not format[2] in SEPARATORS:
            if format[2]=="%":
                raise ValueError(f"Missing separator between '{format[:2]}' and '{format[2:]}'"
                                " in date format string.")
            raise ValueError(f"Invalid separator '{format[2]}' in date format string.")
        
        first_separator = format[2]
        format = format[3:]
        if not format[:2] in elems: 
            raise ValueError(f"Invalid sequence '{format[:2]}' after separator. Use '%d', '%m' or '%Y'.")

        if not format[2] in SEPARATORS:
            if format[2]=="%":
                raise ValueError(f"Missing separator between '{format[:2]}' and '{format[2:]}' in date format string.")
            raise ValueError(f"Invalid separator '{format[2]}' in date format string.")
        if not format[2]==first_separator:
            raise ValueError(f"Two different separators ('{first_separator}' and '{format[2]}')"
                            " found in the passed date format string. Use only"
                            " a single separator {SEPARATORS}.")

        format = format[3:]
        if not format[:2] in elems: 
            raise ValueError(f"Invalid sequence '{format[:2]}' after separator. Use '%d', '%m' or '%Y'.")
        

    DATE_FORMATS:Dict[Locale_Code,str] = {
        "en_us" : "%Y-%m-%d",
        "cs_cz" : "%d.%m.%Y"
    }
        
    @staticmethod
    def default_date(locale_code:Locale_Code)->str:
        return Date_Converter.__date_to_str(
            Date_Converter._get_today(), 
            Date_Converter.DATE_FORMATS[locale_code]
        )

    @staticmethod
    def _get_today()->datetime.date:
        return datetime.date.today()
    
    @staticmethod
    def __date_to_str(date:datetime.date, format:str)->str:
        return date.strftime(format)
    
        

def get_date_converter(user_def_format:str)->Date_Converter:
    Date_Converter._validate_format(user_def_format)
    return Date_Converter(user_def_format)

