import datetime
from re import fullmatch, match


SEPARATORS = (".","_","-"," ")

class Date_Converter:
    def __init__(self,user_format:str)->None:
        self.__format = user_format

    def enter_date(self,readable_date:str)->datetime.date:
        return datetime.datetime.strptime(readable_date, self.__format)
    
    def print_date(self,date_obj:datetime.date)->str:
        return date_obj.strftime(self.__format)


def get_date_converter(user_def_format:str)->Date_Converter:
    __validate_format(user_def_format)
    return Date_Converter(user_def_format)


def __validate_format(format:str)->None:
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