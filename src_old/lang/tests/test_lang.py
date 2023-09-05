import sys
sys.path.insert(1,"src/lang") 

import unittest
import lang


class Test_Language(unittest.TestCase):

    def setUp(self) -> None:
        self.xml_source = "tests"
        self.vocabulary = lang.Vocabulary()
        self.vocabulary.load_xml(self.xml_source,'en_us')

    def test_using_vocabulary_without_not_loaded_xml_source_raises_exception(self):
        new_voc = lang.Vocabulary()
        with self.assertRaises(lang.UninitiallizedVocabulary):
            new_voc.text('Element_from_source_not_loaded')

    def test_parsing_invalid_xml_source(self):
        with self.assertRaises(ValueError):
            self.vocabulary.load_xml(self.xml_source, "invalid_language_code")

    def test_parsing_valid_xml_source(self):
        self.assertEqual(self.vocabulary.text("Food","Fruits","Banana"), "Banana")

    def test_trying_to_access_nonexistent_item(self):
        self.assertRaises(ValueError, self.vocabulary.text,"Food","Clothes") 

    def test_getting_subvocabulary(self):
        subvoc = self.vocabulary.subvocabulary("Food")
        self.assertEqual(subvoc.text("Fruits","Banana"), "Banana")
        fruit_subvoc = self.vocabulary.subvocabulary("Food","Fruits")
        self.assertEqual(fruit_subvoc.text("Banana"), "Banana")



if __name__=="__main__":
    unittest.main()