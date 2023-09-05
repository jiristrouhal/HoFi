import sys
sys.path.insert(1,"src")


import core.tree_templates as tt
import unittest


class Test_Adding_Template(unittest.TestCase):

    def setUp(self) -> None:
        self.app_template = tt.AppTemplate()

    def test_adding_a_template_of_item_with_no_children(self):
        self.app_template.add(tt.NewTemplate('SomeItem', {"name":"New item", "size":15}, children=()))
        self.assertTrue(self.app_template('SomeItem') is not None)
        self.assertEqual(self.app_template('SomeItem').attributes["name"].value, "New item")
        self.assertEqual(self.app_template('SomeItem').attributes["size"].value, 15)
        self.assertEqual(self.app_template('SomeItem').children, ())
        self.assertListEqual(self.app_template.template_tags(), ["SomeItem"])

    def test_adding_template_with_already_taken_tag_is_not_allowed(self):
        self.app_template.add(tt.NewTemplate('tagX', {"name":"New item", "size":15}, children=()))
        self.assertRaises(KeyError, self.app_template.add,
            tt.NewTemplate('tagX', {"name":"New item", "height":4}, children=())
        )
    
    def test_adding_templates_with_identical_tags_is_not_allowed(self):
        self.assertRaises(
            KeyError, 
            self.app_template.add, 
            tt.NewTemplate('tagX', {"name":"New item", "size":15}, children=()),
            tt.NewTemplate('tagX', {"name":"New item", "height":4}, children=())
        )

    def test_adding_a_template_of_item_with_children_of_the_same_type(self):
        self.app_template.add(
            tt.NewTemplate('SomeItem', {"name":"New item", "size":15}, children=('SomeItem',))
        )
        self.assertTrue(self.app_template.template('SomeItem') is not None)

    def test_adding_a_template_of_item_with_children_of_a_diffent_type(self):
        self.app_template.add(
            tt.NewTemplate('SomeItem', {"name":"New item", "size":15}, children=('Child',)),
            tt.NewTemplate('Child', {"name":"New item", "size":15}, children=())
        )
        self.assertListEqual(self.app_template.template_tags(), ["SomeItem", "Child"])

    def test_not_defining_the_child_item_template_raises_error(self):
        self.app_template.clear()
        parent_template = tt.NewTemplate(
                'SomeItem', 
                {"name":"New item", "size":15}, 
                children=('Undefined child template',)
            )
        self.assertRaises(KeyError, self.app_template.add, parent_template) # missing child template

    

class Test_Removing_Template(unittest.TestCase):

    def setUp(self) -> None:
        self.app_template = tt.AppTemplate()

    def test_removing_an_existing_template(self):
        self.app_template = tt.AppTemplate()
        self.app_template.add(tt.NewTemplate('SomeItem', {"name":"New item", "size": 15}, children=()))
        self.app_template.remove('SomeItem')
        self.assertListEqual(self.app_template.template_tags(),[])
        self.assertRaises(KeyError, self.app_template.template, 'SomeItem')

    def test_removing_a_nonexistent_template(self):
        self.assertRaises(KeyError, self.app_template.remove, 'NonexistentItem')

    def test_removing_a_template_used_as_a_child_in_another(self):
        self.app_template.add(
            tt.NewTemplate('A', {"name":"New item", "size": 15}, children=('B',)),
            tt.NewTemplate('B', {"name":"New item", "size": 15}, children=())
        )
        self.assertRaises(Exception, self.app_template.remove, 'B')


class Test_Modifying_Template(unittest.TestCase):

    def setUp(self) -> None:
        self.app_template = tt.AppTemplate()
        self.app_template.add(
            tt.NewTemplate('A', {"name":"New", "size":15}, children=('B','C')),
            tt.NewTemplate('B', {"name":"New", "size":15}, children=('B',)),
            tt.NewTemplate('C', {"name":"New", "size":15}, children=())
        )

    def test_modifying_nonexistent_template_raises_error(self):
        self.assertRaises(KeyError, self.app_template._modify_template,'Nonexistent Template')

    def test_modifying_template_attributes(self):
        self.app_template._modify_template('A', new_attributes={"name":"New", "height":20})
        self.assertEqual(self.app_template('A').attributes["height"].value,20)

    def test_modifying_template_attributes_without_including_name_attribute_raises_error(self):
        self.assertRaises(Exception, self.app_template._modify_template, 'A', {"height":20})

    def test_modifying_template_children(self):
        self.app_template._modify_template('A', new_children=('B',))
        self.assertEqual(self.app_template.template('A').children,('B',))

    def test_adding_undefined_children_raises_error(self):
        self.assertRaises(Exception, self.app_template._modify_template, 'A', {}, ('B','Nonexistent'))


class Test_Locked_Template(unittest.TestCase):

    def setUp(self) -> None:
        self.app_template = tt.AppTemplate()
        self.app_template.add(
            tt.NewTemplate('A', {"name": "New", "size":20}, children=(), locked=True),
            tt.NewTemplate('B', {"name": "New", "size":20}, children=())
        )

    def test_locked_template_cannot_be_removed(self):
        self.assertRaises(tt.TemplateLocked, self.app_template.remove, 'A')

    def test_locked_template_cannot_be_modified(self):
        self.assertRaises(tt.TemplateLocked, self.app_template._modify_template, 'A')

    def test_templates_are_unlocked_by_default(self):
        self.assertFalse(self.app_template('B')._locked)


if __name__=='__main__': unittest.main()