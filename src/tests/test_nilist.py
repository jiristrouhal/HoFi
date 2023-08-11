import sys
sys.path.insert(1,"src")


import src.nlist as nl
import unittest


class NamedThing: 
    def __init__(self,name:str)->None:
        self.name = name


class Test_Modifying_List(unittest.TestCase):

    def setUp(self) -> None:
        self.nlist = nl.NamedItemsList()
        
    
    def test_adding_to_list(self)->None:
        self.nlist.append(NamedThing("Item 1"), NamedThing("Item 2"))
        self.assertListEqual(self.nlist.names, ["Item 1", "Item 2"])

    def test_removing_from_list(self)->None:
        self.nlist.append(NamedThing("Item 1"), NamedThing("Item 2"))
        self.nlist.remove("Item 1")
        self.assertListEqual(self.nlist.names, ["Item 2"])

    def test_removing_nonexistent_item_has_no_effect(self)->None:
        self.nlist.append(NamedThing("Item X"))
        self.nlist.remove("Nonexistent item")
        self.assertListEqual(self.nlist.names, ["Item X"])

    def test_adding_item_with_already_existing_name_makes_the_list_to_run_warning_action(self):

        self.produced_warnings = list()
        # create an example of a warning, that the name of the item is already taken
        def warning_action(*names:str): 
            for name in names: 
                self.produced_warnings.append(f"Name '{name}' is already taken.")

        self.nlist.add_name_warning(warning_action)

        self.nlist.append(NamedThing("Item X"))
        self.nlist.append(NamedThing("Item X"))
        self.assertListEqual(self.nlist.names, ["Item X"])
        self.assertListEqual(self.produced_warnings, ["Name 'Item X' is already taken."])

        

if __name__=="__main__": unittest.main()