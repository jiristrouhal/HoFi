import datetime


class Date_Converter:
    def __init__(self,user_format:str)->None:
        self.__format = user_format

    def enter_date(self,readable_date:str)->datetime.date:
        return datetime.datetime.strptime(readable_date, self.__format)
    
    def print_date(self,date_obj:datetime.date)->str:
        return date_obj.strftime(self.__format)


def get_date_converter(user_def_format:str)->Date_Converter:
    return Date_Converter(user_def_format)
