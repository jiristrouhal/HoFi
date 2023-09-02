import sys 
sys.path.insert(1,"src")

import controls.tree_to_xml as tree_to_xml
import core.tree as treemod
import core.tree_templates as templ
import unittest
import os


class Test_Saving_And_Loading_Trees(unittest.TestCase):

    def setUp(self) -> None:
        self.app_template = treemod.AppTemplate()
        self.app_template.add(
            templ.NewTemplate('Tree',{'name':"New", "weight":123, "height":20}, children=('Branch',)),
            templ.NewTemplate('Branch',{'name':"New", "weight":123}, children=('Branch',)),
        )
        self.converter = tree_to_xml.Tree_XML_Converter(self.app_template)
        self.tree1 = treemod.Tree("Tree 1",tag='Tree',app_template=self.app_template)

    def test_data_file_path_is_always_set_to_existing_directory(self):
        somepath = tree_to_xml.data_file_path("somefile","data/somedirectory")
        self.assertTrue(os.path.isdir(os.path.dirname(somepath)))
    
    def test_empty_tree_after_saving_and_loading_is_unchanged(self):
        self.converter.save_tree(self.tree1)
        tree = self.converter.load_tree("Tree 1")
        self.assertEqual(tree.name, "Tree 1")

    def test_nonempty_tree_after_saving_and_loading_is_unchanged(self):
        self.tree1.new("Branch X",tag='Branch')
        self.tree1.new("Branch Y",tag='Branch')
        self.converter.save_tree(self.tree1)
        tree = self.converter.load_tree("Tree 1")
        self.assertListEqual(tree.children(), ["Branch X","Branch Y"])

    def test_nonempty_tree_with_branches_having_child_branches_is_unchanged_after_saving_and_loading_(self):
        sometree = treemod.Tree("SomeTreeX",tag='Tree',app_template=self.app_template)
        sometree.set_attribute("weight",100)
        sometree.new("Branch X",tag='Branch')
        sometree.new("Small branch","Branch X",tag='Branch')
        sometree.new("Smaller branch","Branch X","Small branch",tag='Branch')
        
        self.converter.save_tree(sometree)
        loaded_tree = self.converter.load_tree("SomeTreeX")
        self.assertEqual(loaded_tree.attributes["weight"].value, 100)
        self.assertListEqual(loaded_tree.children(), ["Branch X"])
        self.assertListEqual(loaded_tree.children("Branch X",), ["Small branch"])
        self.assertListEqual(loaded_tree.children("Branch X","Small branch"), ["Smaller branch"])

    def test_loading_tree_from_nonexistent_path_returns_none(self):
        self.assertEqual(self.converter.load_tree("Nonexistent tree"), None)

    def test_loading_tree_from_xml_sets_attributes_missing_in_xml_compared_to_template_to_default_values(self)->None:
        # save the tree under an old template
        self.tree1.set_attribute("weight",314)
        self.converter.save_tree(self.tree1)
        # modify the template to contain a new attribute with default value '5'
        self.app_template._modify_template('Tree', {'name':"New", "weight":123, "height":20, "new_attribute":5})
        loaded_tree1 = self.converter.load_tree("Tree 1")
        # attributes found in both xml and template are loaded with their saved values
        self.assertEqual(loaded_tree1.attributes["weight"].value, 314)
        # attributes missing in xml are created with default values
        self.assertEqual(loaded_tree1.attributes["new_attribute"].value, 5)

    def test_loading_tree_from_xml_ignores_attributes_not_present_in_the_template(self)->None:
        # save the tree under an old template
        self.tree1.set_attribute("weight",314)
        self.converter.save_tree(self.tree1)
        # remove the attribute 'height' from the 'Tree' template
        self.app_template._modify_template('Tree', {'name':"New", "weight":123})
        loaded_tree1 = self.converter.load_tree("Tree 1")
        # attributes found in both xml and template are loaded with their saved values
        self.assertEqual(loaded_tree1.attributes["weight"].value, 314)
        # attributes missing in template are ignored
        with self.assertRaises(KeyError): loaded_tree1.attributes["height"]

    def test_loading_invalid_xml_file_runs_action(self)->None:
        self.x = 0
        def action()->None: self.x += 1

        self.converter.add_action('invalid_xml', action)
        with open("Invalid_tree_file.xml","w") as f:
            f.write("Some invalid content\n <Not-closed_item>\n")

        self.converter.load_tree("Invalid_tree_file")
        self.assertEqual(self.x, 1)
        self.converter.load_tree("Invalid_tree_file")
        self.assertEqual(self.x, 2)

    def tearDown(self) -> None:
        if os.path.isfile("Invalid_tree_file.xml"):
            os.remove("Invalid_tree_file.xml")


class Test_Saving_And_Loading_Tree_With_Money_Attribute(unittest.TestCase):

    def test_saving_and_loading_tree_with_currency_attribute_keeps_the_amount_and_currency_unchanger(self):
        self.app_template = treemod.AppTemplate("en_us")
        self.app_template.add(
            templ.NewTemplate('Tree', {"name":"Tree","cost":"$1"},children=())
        )
        converter = tree_to_xml.Tree_XML_Converter(self.app_template)
        tree = treemod.Tree("TreeXY",'Tree',app_template=self.app_template)
        tree.set_attribute("cost",10)
        self.assertEqual(tree.attributes["cost"].formatted_value,"$10.00")

        converter.save_tree(tree,".")
        loaded_tree = converter.load_tree("TreeXY",".")
        self.assertEqual(loaded_tree.attributes["cost"].formatted_value,"$10.00")

    def tearDown(self) -> None:
        if os.path.isfile("TreeXY.xml"):
            os.remove("TreeXY.xml")

              

if __name__=="__main__": unittest.main()