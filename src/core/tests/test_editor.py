from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.editor import new_editor, blank_case_template, Case_Template, Editor


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

    def setUp(self) -> None:
        self.case_template = blank_case_template()

    def test_list_of_available_items_to_be_created_is_empty_without_specifying_any_item_template(self):
        editor = new_editor(self.case_template)
        thecase = editor.new_case("Case")
        self.assertEqual(editor.item_types_to_create(thecase), ())

    def test_creating_item_from_a_template(self):
        self.case_template.add_template('Item', {}, (),)
        self.case_template.add_case_child_label('Item')

        editor = new_editor(self.case_template)
        acase = editor.new_case("Case")

        self.assertEqual(editor.item_types_to_create(acase), ('Item',))

        item = editor.new(acase,'Item')
        self.assertTrue(acase.is_ancestor_of(item))
        self.assertEqual(editor.item_types_to_create(item), ())

    def test_adding_item_template_under_empty_label_raises_exception(self):
        self.assertRaises(
            Case_Template.BlankTemplateLabel, 
            self.case_template.add_template, label="", attribute_info={}, child_template_labels=()
        )

    def test_changing_case_template_after_creating_the_editor_does_not_affect_the_editor(self):
        self.case_template.add_template('Item', {}, (),)
        self.case_template.add_case_child_label('Item')
        editor = new_editor(self.case_template)

        self.case_template.add_template('Other Item Type', {}, ())
        self.case_template.add_case_child_label('Other Item Type')
        acase = editor.new_case("Case")

        # the 'Other Item Type' is not included in the editor types
        self.assertEqual(editor.item_types_to_create(acase), ('Item',))

        # the new type is included if the editor is created after adding the type to the case template
        editor_2 = new_editor(self.case_template)
        acase_2 = editor_2.new_case("Case")
        self.assertEqual(editor_2.item_types_to_create(acase_2), ('Item', 'Other Item Type'))

    def test_creating_item_without_existing_template_raises_exception(self):
        self.case_template.add_template('Item', {}, (),)
        self.case_template.add_case_child_label('Item')

        editor = new_editor(self.case_template)
        acase = editor.new_case("Case")

        self.assertRaises(
            Editor.InvalidChildTypeUnderGivenParent,
            editor.new, 
            acase,
            'Nonexistent template label'
        )

    def test_removing_item(self)->None:
        self.case_template.add_template("Item", {}, ())
        self.case_template.add_case_child_label('Item')

        editor = new_editor(self.case_template)
        acase = editor.new_case("Case")
        item = editor.new(acase, "Item")

        self.assertTrue(acase.is_parent_of(item))
        editor.remove(item,acase)
        self.assertFalse(acase.is_parent_of(item))
        

class Test_Managing_Cases(unittest.TestCase):

    def setUp(self) -> None:
        self.case_template = blank_case_template()
        self.editor = new_editor(self.case_template)

    def test_case_name_is_adjusted_if_already_taken(self):
        caseA = self.editor.new_case("Case")
        caseB = self.editor.new_case("Case")
        self.assertEqual(caseA.name, "Case")
        self.assertEqual(caseB.name, "Case (1)")

    def test_deleting_case(self):
        caseA = self.editor.new_case("Case")
        self.assertTrue(self.editor.contains_case(caseA))
        self.editor.remove_case(caseA)
        self.assertFalse(self.editor.contains_case(caseA))

        


if __name__=="__main__": unittest.main()

