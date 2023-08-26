import sys
sys.path.insert(-1, "src")


import unittest
import src.controls.loc.lang as lang


class Test_Language(unittest.TestCase):

    def test_parsing_valid_lang_file_describing_editor_menu(self):
        vocabulary = lang.Vocabulary('en_us')
        self.assertEqual(vocabulary.text("Editor","Right_Click_Menu","Expand_All"), "Expand all")


if __name__=="__main__":
    unittest.main()