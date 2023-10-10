from __future__ import annotations
import sys 
sys.path.insert(1,"src")

import unittest
from src.application.app import App


class Test_Setting_App(unittest.TestCase):

    def setUp(self) -> None:
        self.app = App(locale_code = "cs_cz")

    def test_setting_localization(self):
        self.assertEqual(self.app.locale_code, "cs_cz")
        self.assertEqual(self.app.editor.locale_code, "cs_cz")

    def test_application_settings(self):
        self.app.set('currency','CZK')
        self.assertEqual(self.app.settings('currency'),'CZK')


    
if __name__=="__main__":  unittest.main()
