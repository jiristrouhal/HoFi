import sys
sys.path.insert(0,"src")


import dates
import unittest


class Test_Specifying_Date_Format(unittest.TestCase):


    def test_correct_formats(self)->None:
        conv = dates.Date_Converter("%d.%m.%Y")
        self.assertEqual(
            "12.01.2023", 
            conv.print_date(conv.enter_date("12.01.2023"))
        )
        
        


if __name__=='__main__': unittest.main()