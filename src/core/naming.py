import re


def strip_and_join_spaces(name:str)->str:
    return ' '.join(name.strip().split())


def change_name_if_already_taken(name:str)->str:
    PATTERN = "[\s\S]*\(\s*[\+\-]?\d*\s*\)?\s*" 
    if re.fullmatch(PATTERN,name):
        #remove trailing spaces
        s = name.strip()
        #remove closing parenthesis if present
        if s[-1]==")": s = s[:-1].strip()
        # extract the number inside the parentheses
        number_str = ""
        while re.fullmatch("[\+\-\d]",s[-1]):
            number_str = s[-1]+number_str
            s = s[:-1]
        # increment the extracted number - if the number string is empty, set it to one
        if number_str=="": number_str = "1"
        else:
            number_str = str(int(number_str)+1)
        name = s.strip() + number_str+')'
    else:
        name += " (1)"
    return name
