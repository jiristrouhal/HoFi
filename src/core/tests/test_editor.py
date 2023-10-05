from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.editor import new_editor, blank_case_template, Case_Template, Editor
NBSP = u"\u00A0"

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
        self.case_template.add('Item', {}, (),)
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
            self.case_template.add, label="", attribute_info={}, child_template_labels=()
        )

    def test_adding_nonexistent_case_child_label_raises_exception(self):
        self.assertRaises(
            Case_Template.UndefinedTemplate, 
            self.case_template.add_case_child_label, 
            'Nonexistent_template_label'
        )

    def test_changing_case_template_after_creating_the_editor_does_not_affect_the_editor(self):
        self.case_template.add('Item', {}, (),)
        self.case_template.add_case_child_label('Item')
        editor = new_editor(self.case_template)

        self.case_template.add('Other_Item_Type', {}, ())
        self.case_template.add_case_child_label('Other_Item_Type')
        acase = editor.new_case("Case")

        # the 'Other Item Type' is not included in the editor types
        self.assertEqual(editor.item_types_to_create(acase), ('Item',))

        # the new type is included if the editor is created after adding the type to the case template
        editor_2 = new_editor(self.case_template)
        acase_2 = editor_2.new_case("Case")
        self.assertEqual(editor_2.item_types_to_create(acase_2), ('Item', 'Other_Item_Type'))

    def test_creating_item_without_existing_template_raises_exception(self):
        self.case_template.add('Item', {}, (),)
        self.case_template.add_case_child_label('Item')

        editor = new_editor(self.case_template)
        acase = editor.new_case("Case")

        self.assertRaises(
            Editor.UndefinedTemplate,
            editor.new, 
            acase,
            'Nonexistent template label'
        )

    def test_removing_item(self)->None:
        self.case_template.add("Item", {}, ())
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

    def test_removing_case(self):
        caseA = self.editor.new_case("Case")
        self.assertTrue(self.editor.contains_case(caseA))
        self.editor.remove_case(caseA)
        self.assertFalse(self.editor.contains_case(caseA))

        self.editor.undo()
        self.assertTrue(self.editor.contains_case(caseA))
        self.editor.redo()
        self.assertFalse(self.editor.contains_case(caseA))
        self.editor.undo()
        self.assertTrue(self.editor.contains_case(caseA))

    def test_duplicate_case(self):
        caseA = self.editor.new_case("Case")
        caseA_dupl = caseA.duplicate()
        self.assertTrue(self.editor.contains_case(caseA_dupl))
        self.editor.undo()
        self.assertFalse(self.editor.contains_case(caseA_dupl))
        self.editor.redo()
        self.assertTrue(self.editor.contains_case(caseA_dupl))
        self.assertEqual(caseA_dupl.name,"Case (1)")


from src.core.item import ItemImpl
class Test_Converting_Cases_To_Items_And_Back(unittest.TestCase):

    def setUp(self) -> None:
        self.case_template = blank_case_template()
        self.case_template.add('Item', {}, ('Item',))
        self.case_template.add_case_child_label('Item')
        self.editor = new_editor(self.case_template)

    def test_duplicate_item_as_a_case(self):
        caseA = self.editor.new_case("Case A")
        parent = self.editor.new(caseA,'Item')
        child = self.editor.new(parent,'Item')
        grandchild = self.editor.new(child, 'Item')
        grandchild.rename("Grandchild")

        caseA.rename("Case A_")
        derived_case = self.editor.duplicate_as_case(child)
        self.assertTrue(self.editor.contains_case(derived_case))
        self.assertEqual(derived_case.name, "Item")
        self.assertTrue(derived_case.has_children())

        child_copy = derived_case.pick_child('Item')
        self.assertTrue(child_copy.pick_child("Grandchild") is not ItemImpl.NULL)

    
class Test_Accessing_Item_Attributes_Via_Editor(unittest.TestCase):

    def setUp(self):
        self.case_template = blank_case_template()
        self.attrc = self.case_template.attr

    def test_case_template_collects_attributes_added_via_templates(self):
        self.case_template.add('typeA', {'x':self.attrc.real()}, ())
        self.case_template.add('typeA', {'x':self.attrc.real(),'y':self.attrc.integer()}, ())
        self.assertDictEqual(self.case_template.attributes, {'x':self.attrc.real(), 'y':self.attrc.integer()})

    def test_using_already_used_attribute_with_different_type_in_new_template_raises_exception(self):
        self.case_template.add('typeA', {'x':self.attrc.real()}, ())
        self.assertRaises(
            Case_Template.ReaddingAttributeWithDifferentType, 
            self.case_template.add, 'typeA', {'x':self.attrc.integer()}, ()
        )

    def test_listing_item_attributes(self)->None:
        self.case_template.add('typeA', {'xA':self.attrc.real(), 'yA':self.attrc.real()}, ())
        self.case_template.add('typeB', {'xB':self.attrc.integer()}, ())
        self.case_template.add_case_child_label('typeA', 'typeB')
        editor = new_editor(self.case_template)
        self.assertEqual(editor.attributes, {'xA':self.attrc.real(),'yA':self.attrc.real(),'xB':self.attrc.integer()})

    def test_accessing_attribute_value(self):
        self.case_template.add(
            'Item_with_mass',
            {'mass':self.attrc.quantity(init_value=0,unit='kg')},
            ()
        )
        self.case_template.add(
            'Counter',
            {'count':self.attrc.integer(init_value=0)},
            ()
        )
        self.case_template.add_case_child_label('Item_with_mass', 'Counter')

        editor = new_editor(self.case_template)
        newcase = editor.new_case("Case")
        item = editor.new(newcase, 'Item_with_mass')
        counter = editor.new(newcase, 'Counter')
        item.set("mass",5.5)
        counter.set('count',3)

        self.assertEqual(editor.value(item,'mass',trailing_zeros=False), f"5.5{NBSP}kg")
        self.assertEqual(editor.value(counter,'count'), "3")


class Test_Check_Template_Labels_Do_Not_Contains_Only_Alphanumeric_Characters(unittest.TestCase):
        
    def setUp(self) -> None:
        self.case_template = blank_case_template()

    def test_other_than_alphanumeric_characters_plus_underscore_in_the_template_label_raise_exception(self):
        self.assertRaises(Case_Template.InvalidCharactersInLabel,self.case_template.add,
            'Label with spaces',{}, ()
        )
        self.assertRaises(Case_Template.InvalidCharactersInLabel,self.case_template.add,
            '????',{}, ()
        )

    def test_greek_letters_are_allowed(self):
        self.case_template.add('ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω',{}, ())

    def test_czech_letters_with_diacritics_is_allowed(self):
        self.case_template.add('ůúěščřžýáíéťď',{}, ())
        self.case_template.add('ůúěščřžýáíéťď'.upper(),{}, ())


class Test_Setting_Item_Attribute_Dependency_In_Editor(unittest.TestCase):

    def test_setting_dependency_of_one_of_items_attribute_on_another(self):
        case_template = blank_case_template()
        def square(x:int)->int: return x*x
        case_template.add(
            'Item', 
            {'y':case_template.attr.integer(0), 'x':case_template.attr.integer(2)},
            dependencies=[Case_Template.Dependency('y', square, 'x')]
        )
        case_template.add_case_child_label('Item')
        editor = new_editor(case_template)

        caseA = editor.new_case('Case A')
        item = editor.new(caseA, 'Item')
        item.set('x',3)

        self.assertEqual(item('y'),9)


from src.core.editor import ItemCreator
class Test_Adding_Templates_Of_Items_That_Can_Be_Both_Parents_Of_Each_Other(unittest.TestCase):

    def test_adding_templates_of_items_that_can_be_parents_of_each_other(self):
        case_template = blank_case_template()
        case_template.add('typeA', {}, child_template_labels=('typeB',))
        case_template.add_case_child_label('typeA')
        self.assertRaises(ItemCreator.UndefinedTemplate, new_editor, case_template)

        case_template.add('typeB', {}, child_template_labels=('typeA',))
        editor = new_editor(case_template)


class Test_Saving_And_Loading_Case(unittest.TestCase):

    def test_saving_and_loading_case(self):
        case_template = blank_case_template()
        case_template.add('Item',{},child_template_labels=('Item',))
        case_template.add_case_child_label('Item')
        editor = new_editor(case_template)
        caseA = editor.new_case('Case A')
        item = editor.new(caseA, 'Item')
        item.rename('Item X')




if __name__=="__main__": unittest.main()

