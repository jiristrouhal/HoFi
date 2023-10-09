from __future__ import annotations
import sys 
sys.path.insert(1,"src")

import unittest
from src.application.app import App


class Test_Setting_App(unittest.TestCase):

    def test_setting_localization(self):
        app = App(locale_code = "en_us")
        self.assertEqual(app.locale_code, "en_us")
        


    
if __name__=="__main__":  unittest.main()
