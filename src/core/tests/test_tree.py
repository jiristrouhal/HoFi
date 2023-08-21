import sys 
sys.path.insert(1,"src")

import core.tree as tree
import unittest

class Test_Creating_Tree(unittest.TestCase):

    def setUp(self) -> None:
        tree.tt.clear()
        # add a tree template
        tree.tt.add(
            tree.tt.NewTemplate("Tree",{"name":"New"}, children=("Branch",)),
            tree.tt.NewTemplate("Branch",{"name":"New","weight":10}, children=("Branch",))
        )
        self.tree = tree.Tree("Tree 1",tag="Tree")
        self.tree.new("Branch 1",tag="Branch")

    def test_add_branch_to_a_tree(self):
        self.assertListEqual(self.tree.branches(), ["Branch 1"])

    def test_adding_a_child_branch_to_a_nonexistent_branch_has_no_effect(self):
        self.tree.new("Small branch","Nonexistent branch",tag="Branch")

    def test_remove_branch_from_the_tree(self):
        self.tree.new("Branch 2",tag="Branch")
        self.tree.remove_child("Branch 2")
        self.assertListEqual(self.tree.branches(), ["Branch 1"])

    def test_removing_nonexistent_branch_does_not_affect_the_tree(self):
        self.tree.new("Branch 2",tag="Branch")
        self.tree.remove_child("Branch 3")
        self.assertListEqual(self.tree.branches(), ["Branch 1", "Branch 2"])

    def test_removing_a_branch_with_nonexistent_parent_has_no_effect(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.remove_child("Nonexistent branch","Small branch")
        self.assertListEqual(self.tree.branches("Branch 1"), ["Small branch"])

    def test_removing_child_branch_of_a_child_branch(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.remove_child("Branch 1","Small branch")
        self.assertListEqual(self.tree.branches("Branch 1"), [])

    def test_adding_branch_to_an_existing_branch(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        # The smaller branch is not visible via the tree directly
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        # The smaller branch is visible under the Branch 1
        self.assertListEqual(self.tree.branches("Branch 1"), ["Small branch"])

    def test_branch_with_child_branches_cannot_be_removed(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.remove_child("Branch 1")
        self.assertListEqual(self.tree.branches(),["Branch 1"])

    def test_adding_branch_to_a_child_branch(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.new("Smaller branch", "Branch 1", "Small branch",tag="Branch")
        self.assertListEqual(self.tree.branches("Branch 1",),["Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),["Smaller branch"])

    def test_searching_for_empty_branch_name_returns_none_object(self):
        self.assertTrue(self.tree._find_child() is None)

    def test_moving_branch_to_other_place(self):
        self.tree.new("Small branch", "Branch 1",tag="Branch")
        self.tree.move_child(("Branch 1", "Small branch"), ())
        self.assertListEqual(self.tree.branches(),["Branch 1", "Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1"), [])

    def test_moving_child_of_child_branch_one_level_higher(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.new("Smaller branch","Branch 1", "Small branch",tag="Branch")
        self.tree.move_child(("Branch 1","Small branch","Smaller branch"), ("Branch 1",))
        self.assertListEqual(self.tree.branches("Branch 1"),["Small branch","Smaller branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),[])
    
    def test_moving_branch_onto_itself_does_not_have_any_effect(self):
        self.tree.move_child(("Branch 1",), ("Branch 1",))
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        self.assertListEqual(self.tree.branches("Branch 1"),[])

    def test_moving_branch_under_its_children_does_not_have_any_effect(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.move_child(("Branch 1",), ("Branch 1", "Small branch"))
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"), [])

    def test_moving_child_branch_next_to_its_former_parent_can_be_done(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.move_child(("Branch 1","Small branch"), ())
        self.assertListEqual(self.tree.branches(),["Branch 1", "Small branch"]) 
        self.assertListEqual(self.tree.branches("Branch 1",), [])

    def test_moving_branch_onto_child_of_its_child_does_not_have_effect(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.new("Smaller branch","Branch 1", "Small branch",tag="Branch")
        self.tree.move_child(("Branch 1",), ("Branch 1","Small branch","Smaller branch"))
        self.assertListEqual(self.tree.branches(),["Branch 1"]) 
        self.assertListEqual(self.tree.branches("Branch 1",),["Small branch"])
    
    def test_moving_child_branch_onto_its_child_branch_does_not_have_effect(self):
        self.tree.new("Small branch","Branch 1",tag="Branch")
        self.tree.new("Smaller branch", "Branch 1", "Small branch",tag="Branch")
        self.tree.move_child(("Branch 1","Small branch"), ("Branch 1","Small branch","Smaller branch"))
        self.assertListEqual(self.tree.branches("Branch 1"),["Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),["Smaller branch"])

    def test_creating_branch_with_existing_name_yields_branch_with_adjusted_name(self):
        self.tree.new("Branch 1",tag="Branch")
        self.assertListEqual(self.tree.branches(),["Branch 1", "Branch 1 (1)"])
        self.tree.new("Branch 1 (1)",tag="Branch")
        self.assertListEqual(self.tree.branches(),["Branch 1", "Branch 1 (1)", "Branch 1 (2)"])

    def test_moving_branch_where_its_name_already_exists_will_make_it_rename(self):
        self.tree.new("Branch 1","Branch 1",tag="Branch")
        self.assertListEqual(self.tree.branches("Branch 1"),["Branch 1"])
        self.tree.move_child(("Branch 1","Branch 1"),())
        self.assertListEqual(self.tree.branches("Branch 1"),[])
        # The moved branch 'Branch 1' found itself to be moved into location, where 'Branch 1' already existed,
        # thus, it changed its name to 'Branch 1 (1)'
        self.assertListEqual(self.tree.branches(), ["Branch 1", "Branch 1 (1)"])

    def test_moving_nonexistent_branch_has_no_effect(self):
        self.tree.move_child("Nonexistent branch","")
        self.assertListEqual(self.tree.branches(),["Branch 1"])

    def test_renaming_branch_to_name_that_is_not_already_taken_can_be_done(self):
        self.tree.new("Branch 2",tag="Branch")
        self.tree.rename_child(("Branch 2",),"Branch X")
        self.assertListEqual(self.tree.branches(),["Branch 1","Branch X"])     

    def test_renaming_branch_to_name_already_taken_will_make_it_adjust_its_new_name(self):
        self.tree.new("Branch 2",tag="Branch")
        self.tree.rename_child(("Branch 2",),"Branch 1")
        self.assertListEqual(self.tree.branches(),["Branch 1","Branch 1 (1)"])

    def test_listing_children_of_nonexistent_item_yields_empty_list(self):
        self.assertListEqual(self.tree._list_children("Branch 2", "Nonexistent child of Branch 2", type='all'), [])

    def tearDown(self) -> None:
        tree.tt.clear()


class Test_Actions(unittest.TestCase):

    def setUp(self) -> None:
        tree.tt.clear()
        tree.tt.add(
            tree.tt.NewTemplate("Tree",{"name":"New"},children=("Branch",)),
            tree.tt.NewTemplate("Branch",{"name":"New"},children=("Branch",))
        )
        self.tree = tree.Tree("Tree 1",tag="Tree")
        self.tree.new("Branch X",tag="Branch")
        self.x = 0
    
    def test_add_action_on_adding_new_branch(self):
        def foo(*args): self.x=1

        some_random_id = 132
        self.tree.add_action(some_random_id,'add_branch',foo)
        self.assertEqual(self.x,0)
        self.tree.new("Branch Y",tag="Branch")
        self.assertEqual(self.x,1)

    def test_adding_values_to_branch_data(self):
        self.tree._children[0].add_data("key1", 123)
        self.assertEqual(self.tree._children[0].data["key1"], 123)

    def tearDown(self) -> None:
        tree.tt.clear()


class Test_Adding_Leaf_Type_Item(unittest.TestCase):

    def setUp(self) -> None:
        tree.tt.clear()
        tree.tt.add(
            tree.tt.NewTemplate("Tree",{"name":"New"},children=("Branch","Leaf")),
            tree.tt.NewTemplate("Branch",{"name":"New"},children=("Branch","Leaf")),
            tree.tt.NewTemplate("Leaf",{"name":"New"},children=())
        )
        self.tree = tree.Tree("Tree 1",tag="Tree")
        self.tree.new("Branch X",tag="Branch")
        self.tree.new("Leaf X",tag="Leaf")

    def test_leaves_and_branches_can_be_obtained_separatelly(self):
        self.assertEqual(self.tree.branches(),["Branch X"])
        self.assertEqual(self.tree.leaves(),["Leaf X"])
        
    def test_branches_and_leaves_names_can_be_retrieved_together(self):
        self.assertEqual(self.tree._list_children(type='all'),["Branch X","Leaf X"])

    def test_listing_leaf_children_yields_empty_list(self):
        self.assertListEqual(self.tree._children[1]._list_children(type='all'),[])

    def test_manipulating_leafs_items_has_no_effect(self):
        leaf = self.tree._children[1]
        leaf.new("Leaf's branch",tag="Branch")
        self.assertListEqual(leaf._list_children(type='type'),[])

    def tearDown(self) -> None:
        tree.tt.clear()


class Test_Trees_And_Attributes(unittest.TestCase):

    def setUp(self) -> None:
        tree.tt.clear()
        tree.tt.add(
            tree.tt.NewTemplate("Tree",{"name":"New", "height":20},children=()),
        )
        self.tree = tree.Tree("Tree X", tag="Tree")

    def test_modifying_attribute_value(self):
        self.tree.attributes["height"].set(28)
        self.assertEqual(self.tree.attributes["height"].value, 28)

    def tearDown(self) -> None:
        tree.tt.clear()



class Test_Adding_Children_According_To_Templates(unittest.TestCase):

    def setUp(self) -> None:
        tree.tt.clear()
        tree.tt.add(
            tree.tt.NewTemplate('Tree',{"name":"New"},children=("Branch","Root")),
            tree.tt.NewTemplate('Branch',{"name":"New"},children=("Branch","Leaf")),
            tree.tt.NewTemplate('Leaf',{"name":"New"},children=()),
            tree.tt.NewTemplate('Root',{"name":"New"},children=("Root",)),
        )

    def test_accessing_available_child_element_tags(self)->None:
        treeA = tree.Tree("Tree A", tag="Tree")
        self.assertEqual(treeA.child_tags, ("Branch","Root"))

    def test_adding_the_new_children_using_the_tags(self)->None:
        treeA = tree.Tree("Tree A", tag="Tree")
        treeA.new("Branch B", tag="Branch")
        treeA.new("Leaf X", "Branch", tag='Leaf')
        
    def test_trying_to_add_child_with_template_not_assigned_to_the_parent_template_raises_error(self):
        treeA = tree.Tree("Tree A", tag="Tree")
        treeA.new("Branch B", tag="Branch")
        self.assertRaises(KeyError, treeA.new, "Root R", "Branch B", tag="Root")

    def tearDown(self) -> None:
        tree.tt.clear()


if __name__=="__main__": unittest.main()