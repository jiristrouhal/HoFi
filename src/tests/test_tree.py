import sys 
sys.path.insert(1,"src")

import tree
import unittest

class Test_Creating_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.tree = tree.Tree("Tree 1")
        self.tree.add_branch("Branch 1",attributes={"weight":50})

    def test_add_branch_to_a_tree(self):
        self.assertListEqual(self.tree.branches(), ["Branch 1"])

    def test_adding_a_child_branch_to_a_nonexistent_branch_has_no_effect(self):
        self.tree.add_branch("Small branch","Nonexistent branch",attributes={})

    def test_remove_branch_from_the_tree(self):
        self.tree.add_branch("Branch 2",attributes={"weight":50})
        self.tree.remove_branch("Branch 2")
        self.assertListEqual(self.tree.branches(), ["Branch 1"])

    def test_removing_nonexistent_branch_does_not_affect_the_tree(self):
        self.tree.add_branch("Branch 2",attributes={"weight":25})
        self.tree.remove_branch("Branch 3")
        self.assertListEqual(self.tree.branches(), ["Branch 1", "Branch 2"])

    def test_removing_a_branch_with_nonexistent_parent_has_no_effect(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.remove_branch("Nonexistent branch","Small branch")
        self.assertListEqual(self.tree.branches("Branch 1"), ["Small branch"])

    def test_removing_child_branch_of_a_child_branch(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.remove_branch("Branch 1","Small branch")
        self.assertListEqual(self.tree.branches("Branch 1"), [])

    def test_adding_branch_to_an_existing_branch(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        # The smaller branch is not visible via the tree directly
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        # The smaller branch is visible under the Branch 1
        self.assertListEqual(self.tree.branches("Branch 1"), ["Small branch"])

    def test_branch_with_child_branches_cannot_be_removed(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.remove_branch("Branch 1")
        self.assertListEqual(self.tree.branches(),["Branch 1"])

    def test_adding_branch_to_a_child_branch(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.add_branch("Smaller branch", "Branch 1", "Small branch",attributes={"weight":12})
        self.assertListEqual(self.tree.branches("Branch 1",),["Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),["Smaller branch"])

    def test_searching_for_empty_branch_name_returns_none_object(self):
        self.assertTrue(self.tree._find_branch() is None)

    def test_moving_branch_to_other_place(self):
        self.tree.add_branch("Small branch", "Branch 1",attributes={"weight":25})
        self.tree.move_branch(("Branch 1", "Small branch"), ())
        self.assertListEqual(self.tree.branches(),["Branch 1", "Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1"), [])

    def test_moving_child_of_child_branch_one_level_higher(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.add_branch("Smaller branch","Branch 1", "Small branch",attributes={"weight":12})
        self.tree.move_branch(("Branch 1","Small branch","Smaller branch"), ("Branch 1",))
        self.assertListEqual(self.tree.branches("Branch 1"),["Small branch","Smaller branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),[])
    
    def test_moving_branch_onto_itself_does_not_have_any_effect(self):
        self.tree.move_branch(("Branch 1",), ("Branch 1",))
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        self.assertListEqual(self.tree.branches("Branch 1"),[])

    def test_moving_branch_under_its_children_does_not_have_any_effect(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.move_branch(("Branch 1",), ("Branch 1", "Small branch"))
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"), [])

    def test_moving_child_branch_next_to_its_former_parent_can_be_done(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.move_branch(("Branch 1","Small branch"), ())
        self.assertListEqual(self.tree.branches(),["Branch 1", "Small branch"]) 
        self.assertListEqual(self.tree.branches("Branch 1",), [])

    def test_moving_branch_onto_child_of_its_child_does_not_have_effect(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.add_branch("Smaller branch","Branch 1", "Small branch",attributes={"weight":12})
        self.tree.move_branch(("Branch 1",), ("Branch 1","Small branch","Smaller branch"))
        self.assertListEqual(self.tree.branches(),["Branch 1"]) 
        self.assertListEqual(self.tree.branches("Branch 1",),["Small branch"])
    
    def test_moving_child_branch_onto_its_child_branch_does_not_have_effect(self):
        self.tree.add_branch("Small branch","Branch 1",attributes={"weight":25})
        self.tree.add_branch("Smaller branch", "Branch 1", "Small branch", attributes={"weight":12})
        self.tree.move_branch(("Branch 1","Small branch"), ("Branch 1","Small branch","Smaller branch"))
        self.assertListEqual(self.tree.branches("Branch 1"),["Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),["Smaller branch"])

    def test_creating_branch_with_existing_name_yields_branch_with_adjusted_name(self):
        self.tree.add_branch("Branch 1",attributes={"weight":50})
        self.assertListEqual(self.tree.branches(),["Branch 1", "Branch 1 (1)"])
        self.tree.add_branch("Branch 1 (1)",attributes={"weight":40})
        self.assertListEqual(self.tree.branches(),["Branch 1", "Branch 1 (1)", "Branch 1 (2)"])

    def test_moving_branch_where_its_name_already_exists_will_make_it_rename(self):
        self.tree.add_branch("Branch 1","Branch 1",attributes={"weight":50})
        self.assertListEqual(self.tree.branches("Branch 1"),["Branch 1"])
        self.tree.move_branch(("Branch 1","Branch 1"),())
        self.assertListEqual(self.tree.branches("Branch 1"),[])
        # The moved branch 'Branch 1' found itself to be moved into location, where 'Branch 1' already existed,
        # thus, it changed its name to 'Branch 1 (1)'
        self.assertListEqual(self.tree.branches(), ["Branch 1", "Branch 1 (1)"])

    def test_moving_nonexistent_branch_has_no_effect(self):
        self.tree.move_branch("Nonexistent branch","")
        self.assertListEqual(self.tree.branches(),["Branch 1"])

    def test_renaming_branch_to_name_that_is_not_already_taken_can_be_done(self):
        self.tree.add_branch("Branch 2",attributes={"weight":25})
        self.tree.rename_branch(("Branch 2",),"Branch X")
        self.assertListEqual(self.tree.branches(),["Branch 1","Branch X"])     

    def test_renaming_branch_to_name_already_taken_will_make_it_adjust_its_new_name(self):
        self.tree.add_branch("Branch 2",attributes={"weight":25})
        self.tree.rename_branch(("Branch 2",),"Branch 1")
        self.assertListEqual(self.tree.branches(),["Branch 1","Branch 1 (1)"])

    def test_listing_children_of_nonexistent_item_yields_empty_list(self):
        self.assertListEqual(self.tree._list_children("Branch 2", "Nonexistent child of Branch 2", type='all'), [])


class Test_Actions(unittest.TestCase):

    def setUp(self) -> None:
        self.tree = tree.Tree("Tree 1")
        self.tree.add_branch("Branch X",attributes={})
        self.x = 0
    
    def test_add_action_on_adding_new_branch(self):
        def foo(*args): self.x=1
        self.tree.add_action('add_branch',foo)
        self.assertEqual(self.x,0)
        self.tree.add_branch("Branch Y")
        self.assertEqual(self.x,1)

    def test_adding_values_to_branch_data(self):
        self.tree._children[0].add_data("key1", 123)
        self.assertEqual(self.tree._children[0].data["key1"], 123)

    def test_adding_values_to_branch_data_under_existing_key_raises_error(self):
        self.tree._children[0].add_data("key1", 123)
        self.assertRaises(KeyError, self.tree._children[0].add_data, "key1", 456)


class Test_Adding_Leaf_Type_Item(unittest.TestCase):

    def setUp(self) -> None:
        self.tree = tree.Tree("Tree 1")
        self.tree.add_branch("Branch X")
        self.tree.add_leaf("Leaf X")

    def test_leaves_and_branches_can_be_obtained_separatelly(self):
        self.assertEqual(self.tree.branches(),["Branch X"])
        self.assertEqual(self.tree.leaves(),["Leaf X"])
        
    def test_branches_and_leaves_names_can_be_retrieved_together(self):
        self.assertEqual(self.tree._list_children(type='all'),["Branch X","Leaf X"])

    def test_listing_leaf_children_yields_empty_list(self):
        self.assertListEqual(self.tree._children[1]._list_children(type='all'),[])

    def test_manipulating_leafs_items_has_no_effect(self):
        leaf = self.tree._children[1]
        leaf.add_branch("Leaf's branch")
        self.assertListEqual(leaf._list_children(type='type'),[])


if __name__=="__main__": unittest.main()