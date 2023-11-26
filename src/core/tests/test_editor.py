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

        self.assertEqual(editor.print(item,'mass',trailing_zeros=False), f"5.5{NBSP}kg")
        self.assertEqual(editor.print(counter,'count'), "3")


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

    DIRPATH = "./__test_saving_case_1"
    def setUp(self) -> None: # pragma: no cover
        build_dir(self.DIRPATH)
        self.case_template = blank_case_template()
        self.case_template.add('Item',{},child_template_labels=('Item',))
        self.case_template.add_case_child_label('Item')

        self.editor = new_editor(self.case_template)
        self.editor.set_dir_path(self.DIRPATH)

        self.caseA = self.editor.new_case('Case A')
        self.item = self.editor.new(self.caseA,'Item')
        self.item.rename('Item X')

    def test_saving_and_loading_case(self):
        self.editor.save(self.caseA, 'xml')
        self.editor.remove_case(self.caseA)
        self.assertFalse(self.editor.contains_case(self.caseA))

        loaded_case = self.editor.load_case(self.DIRPATH,"Case A","xml")
        self.assertTrue(self.editor.contains_case(loaded_case))
        self.assertFalse(loaded_case.pick_child('Item X').is_null())

    def test_saving_case_as_a_case_is_equivalent_to_calling_save_method(self):
        self.editor.save_as_case(self.caseA, 'xml')
        self.editor.remove_case(self.caseA)
        loaded_case = self.editor.load_case(self.DIRPATH,"Case A","xml")
        self.assertTrue(self.editor.contains_case(loaded_case))

    def test_saving_and_loading_item_as_a_case(self):
        self.editor.save_as_case(self.item,'xml')
        loaded_case = self.editor.load_case(self.DIRPATH, "Item X", "xml")
        self.assertTrue(self.editor.contains_case(loaded_case))
        self.assertFalse(loaded_case.pick_child('Item X').is_null())

        self.editor.undo()
        self.assertFalse(self.editor.contains_case(loaded_case))
        self.editor.redo()
        self.assertTrue(self.editor.contains_case(loaded_case))
        self.editor.undo()
        self.assertFalse(self.editor.contains_case(loaded_case))

    def tearDown(self) -> None: # pragma: no cover
        remove_dir(self.DIRPATH)


class Test_Setting_Up_Under_Which_Parents_Item_Can_Be_Inserted(unittest.TestCase):

    def setUp(self) -> None:
        self.case_template = blank_case_template()
        self.case_template.add('folder',{},('file','folder'))
        self.case_template.add('file', {}, ())
        self.case_template.add_case_child_label('folder')

    def test_setting_up_insertable_type_of_item(self):
        self.case_template.set_insertable('folder') 
        self.editor = new_editor(self.case_template)
        self.assertEqual(self.editor.insertable, 'folder')

    def test_setting_up_insertable_for_which_template_does_not_exist_raises_exception(self):
        self.assertRaises(
            Case_Template.UndefinedTemplate, 
            self.case_template.set_insertable, 'nonexistent type'
        ) 

    def test_determining_if_insertable_can_be_inserted_under_given_item_type(self):
        self.case_template.set_insertable('folder')
        self.editor = new_editor(self.case_template)
        case = self.editor.new_case('CaseX')
        folder = self.editor.new(case,'folder')
        file = self.editor.new(folder,'file')
        self.assertTrue(self.editor.can_insert_under(case))
        self.assertTrue(self.editor.can_insert_under(folder))
        self.assertFalse(self.editor.can_insert_under(file))


class Test_Saving_And_Importing_Items(unittest.TestCase):

    DIRPATH = "./__test_saving_case_2"
    def setUp(self) -> None: # pragma: no cover
        build_dir(self.DIRPATH)
        self.case_template = blank_case_template()
        self.case_template.add('can_be_child_of_case', {}, ('cannot_be_child_of_case',))
        self.case_template.add('cannot_be_child_of_case', {})
        self.case_template.add_case_child_label('can_be_child_of_case')

    def test_cannot_save_as_item_if_no_insertable_item_type_was_set_in_case_template(self):
        editor = new_editor(self.case_template)
        somecase = editor.new_case("Case")
        someitem = editor.new(somecase, "can_be_child_of_case")
        self.assertFalse(editor.can_save_as_item(someitem))
        self.assertRaises(Editor.CannotSaveAsItem, editor.save, someitem, "xml")

    def test_item_can_be_saved_and_loaded_if_its_type_was_specified_as_insertable(self):
        self.case_template.set_insertable('can_be_child_of_case')
        editor = new_editor(self.case_template)
        editor.set_dir_path(self.DIRPATH)
        somecase = editor.new_case("Case")
        someitem = editor.new(somecase, "can_be_child_of_case")
        someitem.rename("Some Item")
        self.assertTrue(editor.can_save_as_item(someitem))
        editor.save(someitem, "xml")
        somecase.leave(someitem)

        self.assertTrue(somecase.pick_child("Some Item").is_null())
        editor.insert_from_file(somecase,self.DIRPATH,"Some Item", "xml")
        self.assertFalse(somecase.pick_child("Some Item").is_null())

    def test_inserting_insertable_item_under_parent_for_which_insertable_is_not_specified_as_child_type_raises_exception(self):
        self.case_template.set_insertable("cannot_be_child_of_case")
        editor = new_editor(self.case_template)
        editor.set_dir_path(self.DIRPATH)

        somecase = editor.new_case("Case")
        itemA = editor.new(somecase, "can_be_child_of_case")
        itemB = editor.new(itemA, "cannot_be_child_of_case")
        itemA.rename("Item A")
        itemB.rename("Item B")
        self.assertFalse(editor.can_save_as_item(itemA))
        self.assertTrue(editor.can_save_as_item(itemB))
        editor.save(itemB, "xml")
        itemA.leave(itemB)

        self.assertTrue(itemA.pick_child("Item B").is_null())
        editor.insert_from_file(itemA, self.DIRPATH, "Item B", "xml")
        self.assertFalse(itemA.pick_child("Item B").is_null())
        editor.undo()
        self.assertTrue(itemA.pick_child("Item B").is_null())
        editor.redo()
        self.assertFalse(itemA.pick_child("Item B").is_null())

        self.assertRaises(
            Editor.CannotInsertItemUnderSelectedParent,
            editor.insert_from_file, somecase, self.DIRPATH, "Item B", "xml"
        )

    def test_cannot_insert_under_item_without_child_of_any_type_allowed(self):
        self.case_template.set_insertable("cannot_be_child_of_case")
        editor = new_editor(self.case_template)
        editor.set_dir_path(self.DIRPATH)
        somecase = editor.new_case("Some Case")
        itemA = editor.new(somecase, 'can_be_child_of_case')
        itemB = editor.new(itemA, 'cannot_be_child_of_case')
        self.assertFalse(editor.can_insert_under(itemB))

    def tearDown(self) -> None: # pragma: no cover
        remove_dir(self.DIRPATH)


class Test_Creating_New_Items_Of_Specified_Types(unittest.TestCase):

    def setUp(self) -> None:
        self.case_template = blank_case_template()
        self.case_template.add("typeA",{},('typeB',))
        self.case_template.add('typeB',{},())
        self.case_template.add_case_child_label('typeA')
        self.editor = new_editor(self.case_template)
        self.case = self.editor.new_case('Case')

    def test_listing_of_available_types_to_be_created_under_given_parent(self):
        itemA = self.editor.new(self.case, 'typeA')
        self.assertEqual(self.editor.item_types_to_create(itemA), ('typeB',))
        itemB = self.editor.new(itemA, 'typeB')
        self.assertEqual(self.editor.item_types_to_create(itemB), ())

    def test_trying_to_create_item_of_type_unavailable_for_current_parent_raises_exception(self):
        self.assertRaises(
            Editor.InvalidChildTypeUnderGivenParent,
            self.editor.new, self.case, 'typeB'
        )


class Test_Import_And_Export_Of_Case_With_Single_Level_Of_Descendants_With_Quantity_Attribute(unittest.TestCase):

    DIRPATH = "./__test_dir_5"

    def setUp(self) -> None: # pragma: no cover
        build_dir(self.DIRPATH)

    def test_saving_and_loading_case_with_child_with_quantity_attribute_with_nonempty_default_prefix(self):
        case_template = blank_case_template()
        mass = case_template.attr.quantity('kg', exponents={'k':3, 'm':-3})
        case_template.add('Item_Type', {"mass":mass}, ('Item_Type',))
        case_template.add_case_child_label("Item_Type")
        editor = new_editor(case_template)
        editor.set_dir_path(self.DIRPATH)

        case = editor.new_case("Assembly")
        item = editor.new(case, "Item_Type")

        item.rename("TheItem")
        item.set("mass", 2)
        item.attribute("mass").set_prefix("")
        self.assertEqual(item.attribute("mass").print(), f"2000{NBSP}g")
        self.assertEqual(item("mass"), 2)
        editor.save_as_case(case, "xml")

        loaded_case = editor.load_case(self.DIRPATH, name="Assembly",ftype="xml")
        loaded_item = list(loaded_case.children)[-1]
        self.assertEqual(loaded_item.attribute("mass").print(), f"2000{NBSP}g")
        self.assertEqual(loaded_item("mass"), 2)

    def tearDown(self) -> None: # pragma: no cover
        remove_dir(self.DIRPATH)

import os
def build_dir(dirpath:str)->None: # pragma: no cover
    if not os.path.isdir(dirpath): 
        os.mkdir(dirpath)

def remove_dir(dirpath:str)->None: # pragma: no cover
    if os.path.isdir(dirpath):
        for f in os.listdir(dirpath): 
            os.remove(os.path.join(dirpath,f))
            pass
        os.rmdir(dirpath)


class Test_Copying_Item(unittest.TestCase):

    def setUp(self) -> None:
        ct = blank_case_template()
        ct.add("Item", {"mass":ct.attr.quantity("kg", {"k":3})}, ("Item","Thing"))
        ct.add("Thing", {}, ())
        ct.set_case_template({},("Item",))
        self.editor = new_editor(ct)
        self.new_case = self.editor.new_case("New case")
        self.item = self.editor.new(self.new_case, "Item")
        self.other_item = self.editor.new(self.new_case, "Item")
        self.other_item.rename("Other Item")

    def test_copying_item(self)->None:
        self.assertTrue(self.editor.item_to_paste is None)
        self.editor.copy(self.item)
        self.assertTrue(self.editor.item_to_paste is not None)
        item_copy = self.editor.item_to_paste
        self.editor.paste_under(self.other_item)
        self.assertTrue(self.other_item.is_parent_of(item_copy))
    
    def test_item_to_paste_is_cleared_after_pasting(self):
        self.editor.copy(self.item)
        self.editor.paste_under(self.other_item)
        self.assertTrue(self.editor.item_to_paste is None)

    def test_pasting_has_no_effect_if_nothing_was_copied(self):
        self.editor.paste_under(self.other_item)
        self.assertFalse(self.other_item.has_children())
    
    def test_pasting_under_itemX_that_cannot_be_the_parent_causes_pasting_under_the_itemXs_parent(self):
        thing_that_cannot_be_a_parrent = self.editor.new(self.other_item, "Thing")
        self.editor.copy(self.item)
        item_copy = self.editor.item_to_paste
        self.editor.paste_under(thing_that_cannot_be_a_parrent)
        self.assertFalse(thing_that_cannot_be_a_parrent.is_parent_of(item_copy))
        self.assertTrue(thing_that_cannot_be_a_parrent.parent.is_parent_of(item_copy))

    def test_pasting_under_case_which_cannot_be_the_parent_has_no_effect(self):
        thing = self.editor.new(self.other_item, "Thing")
        self.editor.copy(thing)
        thing_copy = self.editor.item_to_paste

        self.assertFalse(self.editor.can_paste_under_or_next_to(thing_copy, self.new_case))
        self.editor.paste_under(self.new_case)
        self.assertFalse(self.new_case.is_parent_of(thing_copy))
        self.assertTrue(self.editor.item_to_paste is not None)


if __name__=="__main__": 
    unittest.main()
