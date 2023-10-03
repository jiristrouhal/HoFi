from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.editor import new_editor, blank_case_template


class Test_Specifying_Case_Template(unittest.TestCase):

    def test_creating_case_template_and_passing_to_editor(self)->None:
        case_templ = blank_case_template()


class Test_Creating_Case(unittest.TestCase):

    def setUp(self) -> None:
        case_templ = blank_case_template()
        self.editor = new_editor(case_templ)
        self.case = self.editor.new_case("New Case")

    def test_creating_case(self):
        self.assertEqual(self.case.name, "New Case")
    
    def test_undo_and_redo_renaming_case(self):
        self.case.rename("Case A")
        self.assertEqual(self.case.name, "Case A")
        self.editor.undo()
        self.assertEqual(self.case.name, "New Case")
        self.editor.redo()
        self.assertEqual(self.case.name, "Case A")


class Test_Creating_Item_Under_Case(unittest.TestCase):

    def test_list_of_available_items_to_be_created_is_empty_without_specifying_any_item_template(self):
        case_templ = blank_case_template()
        editor = new_editor(case_templ)
        thecase = editor.new_case("Case")
        self.assertEqual(editor.item_types_to_create(thecase), ())

    def test_creating_item_from_a_template(self):
        case_templ = blank_case_template()

        case_templ.add_template('Item', {}, (),)
        case_templ.add_case_child_label('Item')

        editor = new_editor(case_templ)
        thecase = editor.new_case("Case")

        self.assertEqual(editor.item_types_to_create(thecase), ('Item',))

        item = editor.new(thecase,'Item')
        self.assertTrue(thecase.contains(item))
 

if __name__=="__main__": unittest.main()

