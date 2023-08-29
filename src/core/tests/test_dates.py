import sys
sys.path.insert(0,"src")


import core.dates as dates
import unittest



class Test_Specifying_Date_Format(unittest.TestCase):

    correct_dates = ["01.01.2023", "31.12.2023", "01.01.2024", "29.02.2024", "05.04.2023"]
    incorrect_dates = ["32.01.2023", "29.02.2023", "30.02.2024", "00.01.2022", "4.2023"]


    def test_correct_dates_with_corresponding_correct_format_string(self)->None:
        conv = dates.Date_Converter('cs_cz')
        for date in self.correct_dates:
            self.assertEqual(
                date, 
                conv.print_date(conv.enter_date(date))
            )

    def test_incorrect_dates_and_correct_format_string(self)->None:
        conv = dates.Date_Converter('en_us')
        conv.set("%d.%m.%Y")
        for date in self.incorrect_dates:
            self.assertRaises(ValueError, conv.enter_date, date)

    def test_incorrect_format_string(self)->None:
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%a.%b.%Y")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%m.%Y")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%d.%Y")

    def test_varying_valid_date_separators_in_format_string(self)->None:
        for sep in ('.','-','_',' '):
            conv = dates.Date_Converter._validate_format(f"%d{sep}%m{sep}%Y")

    def test_varying_invalid_date_separators_in_format_string(self)->None:
        for sep in ('..', '---', '', '\t', '       ',''):
            self.assertRaises(ValueError, dates.Date_Converter._validate_format, f"%d{sep}%m{sep}%Y")

    def test_missing_separators_in_date_format_string_raise_error(self):
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%Y%m-%d")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%Y.%m%d")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%Y.%mb%d")

    def test_double_separator_in_date_format_string_raise_error(self):
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%Y..%m.%d")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%Y.%m..%d")

    def test_incomplete_date_format_string_raises_error(self):
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%Y.%m")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%Y.%m.")

    def test_two_distinct_separators_are_not_allowed(self)->None:
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%d.%m-%Y")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%m_%d.%Y")
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, "%d.%m%Y")
    
    def test_date_format_string_must_start_with_percent(self):
        self.assertRaises(ValueError, dates.Date_Converter._validate_format, ".%d.%Y.%m")


from re import fullmatch
class Test_Default_Dates(unittest.TestCase):

    def test_default_date_with_given_locale_codes_returns_todays_date_string_propertly_formatted(self):

        date_str1 = dates.default_date(locale_code='cs_cz')
        date_str2 = dates.default_date(locale_code='en_us')

        self.assertTrue(fullmatch("\d{2}\.\d{2}\.\d{4}",date_str1) is not None)
        self.assertTrue(fullmatch("\d{4}\-\d{2}\-\d{2}",date_str2) is not None)


if __name__=='__main__': unittest.main()