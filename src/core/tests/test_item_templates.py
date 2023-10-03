from __future__ import annotations


import sys 
sys.path.insert(1,"src")


import unittest
from src.core.item import ItemCreator, Item, ItemImpl


class Test_Adding_Item_Template(unittest.TestCase):

    def setUp(self) -> None:
        self.mg = ItemCreator()

    def test_template_of_item_without_attributes_and_children(self):
        self.mg.add_template('Item')
        item = self.mg.from_template('Item')
        self.assertEqual(item.name, 'Item')

    def test_name_of_template_specifies_item_type(self):
        self.mg.add_template('Item')
        item = self.mg.from_template('Item')
        self.assertEqual(item.itype, "Item")
    
    def test_template_of_item_with_attributes(self):
        self.mg.add_template('Item', {'x':'integer'})
        itemA = self.mg.from_template('Item')
        itemB = self.mg.from_template('Item')
        itemA.set('x',5)
        itemB.set('x',-1)

        self.assertEqual(itemA('x'),5)
        self.assertEqual(itemB('x'),-1)


class Test_Specifying_Children_Types(unittest.TestCase):
    
    def setUp(self) -> None:
        self.mg = ItemCreator()

    def test_no_children_are_specified(self):
        self.mg.add_template('Item', child_itypes=())
        item = self.mg.from_template('Item')
        self.assertEqual(item.child_itypes, ())
        # attempt to adopt the child with type not included in child_itypes raises exception
        itemB = self.mg.from_template('Item')
        self.assertRaises(Item.CannotAdoptItemOfType,item.adopt, itemB)
    
    def test_specifyinging_single_child_item_type(self):
        self.mg.add_template('Item', child_itypes=('Item',))
        item = self.mg.from_template('Item')
        self.assertEqual(item.child_itypes, ('Item',))

        itemB = self.mg.from_template('Item')
        item.adopt(itemB)
        self.assertTrue(item.is_parent_of(itemB))


class Test_Checking_Template_Existence(unittest.TestCase):

    def test_adding_child_itype_without_corresponding_template_raises_exception(self):
        mg = ItemCreator()
        self.assertRaises(ItemCreator.UndefinedTemplate, mg.add_template, 'Parent', child_itypes=('Child',))
        # the Child template must to be added first
        mg.add_template('Child')
        mg.add_template('Parent',child_itypes=('Child',))
        self.assertEqual(mg.from_template('Parent').child_itypes, ('Child',))


if __name__=="__main__": unittest.main()

