import sys
sys.path.insert(0,"src")


import dates
import unittest



class Test_Specifying_Date_Format(unittest.TestCase):

    correct_dates = ["01.01.2023", "31.12.2023", "01.01.2024", "29.02.2024", "05.04.2023"]
    incorrect_dates = ["32.01.2023", "29.02.2023", "30.02.2024", "00.01.2022", "4.2023"]


    def test_correct_dates_with_corresponding_correct_format_string(self)->None:
        conv = dates.get_date_converter("%d.%m.%Y")
        for date in self.correct_dates:
            self.assertEqual(
                date, 
                conv.print_date(conv.enter_date(date))
            )

    def test_incorrect_dates_and_correct_format_string(self)->None:
        conv = dates.get_date_converter("%d.%m.%Y")
        for date in self.incorrect_dates:
            self.assertRaises(ValueError, conv.enter_date, date)

    def test_incorrect_format_string(self)->None:
        self.assertRaises(ValueError, dates.get_date_converter, "%a.%b.%Y")
        self.assertRaises(ValueError, dates.get_date_converter, "%m.%Y")
        self.assertRaises(ValueError, dates.get_date_converter, "%d.%Y")

    def test_varying_valid_date_separators_in_format_string(self)->None:
        for sep in ('.','-','_',' '):
            conv = dates.get_date_converter(f"%d{sep}%m{sep}%Y")

    def test_varying_invalid_date_separators_in_format_string(self)->None:
        for sep in ('..', '---', '', '\t', '       ',''):
            self.assertRaises(ValueError, dates.get_date_converter, f"%d{sep}%m{sep}%Y")

    def test_missing_separators_in_date_format_string_raise_error(self):
        self.assertRaises(ValueError, dates.get_date_converter, "%Y%m-%d")
        self.assertRaises(ValueError, dates.get_date_converter, "%Y.%m%d")
        self.assertRaises(ValueError, dates.get_date_converter, "%Y.%mb%d")

    def test_double_separator_in_date_format_string_raise_error(self):
        self.assertRaises(ValueError, dates.get_date_converter, "%Y..%m.%d")
        self.assertRaises(ValueError, dates.get_date_converter, "%Y.%m..%d")

    def test_incomplete_date_format_string_raises_error(self):
        self.assertRaises(ValueError, dates.get_date_converter, "%Y.%m")
        self.assertRaises(ValueError, dates.get_date_converter, "%Y.%m.")

    def test_two_distinct_separators_are_not_allowed(self)->None:
        self.assertRaises(ValueError, dates.get_date_converter, "%d.%m-%Y")
        self.assertRaises(ValueError, dates.get_date_converter, "%m_%d.%Y")
        self.assertRaises(ValueError, dates.get_date_converter, "%d.%m%Y")
    
    def test_date_format_string_must_start_with_percent(self):
        self.assertRaises(ValueError, dates.get_date_converter, ".%d.%Y.%m")


if __name__=='__main__': unittest.main()