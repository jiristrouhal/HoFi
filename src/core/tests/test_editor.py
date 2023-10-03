from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.editor import new_case_template, new_editor, Editor, Case_Template


class Test_Creating_Case_Template(unittest.TestCase):

    def setUp(self) -> None:
        self.ctempl = new_case_template()

    def test_adding_item_template(self):
        self.ctempl.add_template('Item')
        self.assertEqual(self.ctempl.templates, ('Item',))

    def test_repeatedly_adding_template_with_the_same_name_raises_exception(self)->None:
        self.ctempl.add_template('Item')
        self.assertRaises(Case_Template.TemplateAlreadyDefined, self.ctempl.add_template, 'Item')

    


class Test_Using_Case_Template_To_Create_Case(unittest.TestCase):

    def test_creating_new_case(self):
        editor = new_editor()
        ctempl = new_case_template()
        editor.set_case_template(ctempl)
        newcase = editor.new_case('New Case')
        self.assertEqual(newcase.name, 'New Case')

    def test_creating_case_without_specifying_case_template_raises_exception(self)->None:
        editor = new_editor()
        self.assertRaises(Editor.CaseTemplateNotSet, editor.new_case, 'New Case')


if __name__=="__main__": unittest.main()

