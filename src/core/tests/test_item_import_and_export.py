from __future__ import annotations
import sys 
sys.path.insert(1,"src")
import os


import unittest
from src.core.item import ItemCreator, Item, ItemImpl


class Test_Setting_File_Path_For_Item_Saving_And_Loading(unittest.TestCase):

    def setUp(self) -> None:
        os.mkdir("./__test_dir")

    def test_setting_file_path_for_export_and_import_of_items(self):
        cr = ItemCreator()
        cr.set_file_path("./__test_dir")
        self.assertEqual(cr.file_path, "./__test_dir")
    
    def test_setting_file_path_to_nonexistent_directory_raises_exception(self):
        cr = ItemCreator()
        self.assertRaises(
            ItemCreator.NonexistentDirectory, 
            cr.set_file_path, 
            "./__$nonexistent_directory__"
        )

    def tearDown(self):
        if os.path.isdir("./__test_dir"): 
            os.rmdir("./__test_dir")


class Test_Saving_Items_As_XML(unittest.TestCase):

    def setUp(self) -> None: # pragma: no cover
        if not os.path.isdir("./__test_dir_2"): 
            os.mkdir("./__test_dir_2")
        self.cr = ItemCreator()
        self.cr.set_file_path("./__test_dir_2")

    def test_saving_single_item_without_assigned_template_raises_exception(self)->None:
        item = self.cr.new("Item", {"x":"integer"})
        self.assertRaises(ItemCreator.NoTemplateIsAssigned, self.cr.save, item,"xml")

    def test_saving_single_item_as_xml(self)->None:
        self.cr.add_template('Item_X', {"x":self.cr.attr.integer(3)})
        item = self.cr.from_template("Item_X")
        self.cr.save(item,"xml")
        filepath = "./__test_dir_2/Item_X.xml"
        file_was_created = os.path.isfile(filepath)
        if file_was_created: 
            os.remove(filepath)   

        self.assertTrue(file_was_created)
        
    def tearDown(self) -> None: # pragma: no cover
        if os.path.isdir("./__test_dir_2"): 
            os.rmdir("./__test_dir_2")


from decimal import Decimal
class Test_Loading_Item_From_XML(unittest.TestCase):

    DIRPATH = "./__test_dir_3"

    def setUp(self) -> None: # pragma: no cover
        if not os.path.isdir(self.DIRPATH): 
            os.mkdir(self.DIRPATH)
        self.cr = ItemCreator()
        self.cr.set_file_path(self.DIRPATH)
        self.cr.add_template(
            'Item', 
            {
                'count':self.cr.attr.integer(0), 
                'description':self.cr.attr.text("..."),
                'weight':self.cr.attr.quantity("kg")
            }
        )
        self.templ_item = self.cr.from_template('Item')
        self.templ_item.set('count',7)
        self.templ_item.set('description','This is the description.')
        self.templ_item.set('weight', 5)
        self.cr.save(self.templ_item,"xml")

    def test_loading_nonexistent_item_raises_exception(self):
        self.assertRaises(
            ItemCreator.FileDoesNotExist, 
            self.cr.load,
            self.DIRPATH,
            "Nonexistent file",
            "xml"
        )

    def test_loading_item_without_existing_template_raises_exception(self):
        other_cr = ItemCreator() # this creator is missing the template 'Item' required for loading
        self.assertRaises(
            ItemCreator.NoTemplateAvailable,
            other_cr.load, dirpath=self.DIRPATH, name='Item', ftype="xml"
        )

    def test_loading_item(self):
        item = self.cr.load(self.DIRPATH, "Item", "xml")
        self.assertEqual(item.name, "Item")
        self.assertEqual(item('count'),7)
        self.assertEqual(item('description'),'This is the description.')
        self.assertEqual(item('weight'),5)

    def tearDown(self) -> None:
        if os.path.isdir(self.DIRPATH):
            for f in os.listdir(self.DIRPATH): 
                os.remove(os.path.join(self.DIRPATH,f))
            os.rmdir(self.DIRPATH)


if __name__=="__main__": unittest.main()

