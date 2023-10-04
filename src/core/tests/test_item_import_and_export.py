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



if __name__=="__main__": unittest.main()

