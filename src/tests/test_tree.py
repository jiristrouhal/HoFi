import sys 
sys.path.insert(1,"src")

import tree
import unittest

class Test_Creating_Tree(unittest.TestCase):

    def setUp(self) -> None:
        self.tree = tree.Tree()
        self.tree.add_branch(tree.Branch(name="Branch 1", weight=50, length=120))

    def test_add_branch_to_a_tree(self):
        self.assertListEqual(self.tree.branches(), ["Branch 1"])

    def test_remove_branch_from_the_tree(self):
        self.tree.add_branch(tree.Branch(name="Branch 2", weight=50, length=120))
        removed_branch = self.tree.remove_branch("Branch 2")
        self.assertListEqual(self.tree.branches(), ["Branch 1"])
        self.assertTrue(removed_branch is not None)
        self.assertEqual(removed_branch.name, "Branch 2")

    def test_removing_nonexistent_branch_does_not_affect_the_tree(self):
        self.tree.add_branch(tree.Branch(name="Branch 2", weight=50, length=120))
        removed_branch = self.tree.remove_branch("Branch 3")
        self.assertListEqual(self.tree.branches(), ["Branch 1", "Branch 2"])
        self.assertTrue(removed_branch is None)

    def test_adding_branch_to_an_existing_branch(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=80), "Branch 1")
        # The smaller branch is not visible via the tree directly
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        # The smaller branch is visible under the Branch 1
        self.assertListEqual(self.tree.branches("Branch 1"), ["Small branch"])

    def test_branch_with_child_branches_cannot_be_removed(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=80), "Branch 1")
        self.tree.remove_branch("Branch 1")
        self.assertListEqual(self.tree.branches(),["Branch 1"])

    def test_adding_branch_to_a_child_branch(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=70), "Branch 1")
        self.tree.add_branch(tree.Branch(name="Smaller branch", weight=12, length=40), "Branch 1", "Small branch")
        self.assertListEqual(self.tree.branches("Branch 1",),["Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),["Smaller branch"])

    def test_searching_for_empty_branch_name_returns_none_object(self):
        self.assertTrue(self.tree._find_branch() is None)

    def test_moving_branch_to_other_place(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=70), "Branch 1")
        self.tree.move_branch(("Branch 1", "Small branch"), ())
        self.assertListEqual(self.tree.branches(),["Branch 1", "Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1"), [])

    def test_moving_child_of_child_branch_one_level_higher(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=70), "Branch 1")
        self.tree.add_branch(tree.Branch(name="Smaller branch", weight=12, length=40), "Branch 1", "Small branch")
        self.tree.move_branch(("Branch 1","Small branch","Smaller branch"), ("Branch 1",))
        self.assertListEqual(self.tree.branches("Branch 1"),["Small branch","Smaller branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),[])
    
    def test_moving_branch_onto_itself_does_not_have_any_effect(self):
        self.tree.move_branch(("Branch 1",), ("Branch 1",))
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        self.assertListEqual(self.tree.branches("Branch 1"),[])

    def test_moving_branch_under_its_children_does_not_have_any_effect(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=70), "Branch 1")
        self.tree.move_branch(("Branch 1",), ("Branch 1", "Small branch"))
        self.assertListEqual(self.tree.branches(),["Branch 1"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"), [])

    def test_moving_child_branch_next_to_its_former_parent_can_be_done(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=70), "Branch 1")
        self.tree.move_branch(("Branch 1","Small branch"), ())
        self.assertListEqual(self.tree.branches(),["Branch 1", "Small branch"]) 
        self.assertListEqual(self.tree.branches("Branch 1",), [])

    def test_moving_branch_onto_child_of_its_child_does_not_have_effect(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=70), "Branch 1")
        self.tree.add_branch(tree.Branch(name="Smaller branch", weight=12, length=40), "Branch 1", "Small branch")
        self.tree.move_branch(("Branch 1",), ("Branch 1","Small branch","Smaller branch"))
        self.assertListEqual(self.tree.branches(),["Branch 1"]) 
        self.assertListEqual(self.tree.branches("Branch 1",),["Small branch"])
    
    def test_moving_child_branch_onto_its_child_branch_does_not_have_effect(self):
        self.tree.add_branch(tree.Branch(name="Small branch", weight=25, length=70), "Branch 1")
        self.tree.add_branch(tree.Branch(name="Smaller branch", weight=12, length=40), "Branch 1", "Small branch")
        self.tree.move_branch(("Branch 1","Small branch"), ("Branch 1","Small branch","Smaller branch"))
        self.assertListEqual(self.tree.branches("Branch 1"),["Small branch"])
        self.assertListEqual(self.tree.branches("Branch 1","Small branch"),["Smaller branch"])

    def test_creating_branch_with_existing_name_yields_branch_with_adjusted_name(self):
        self.tree.add_branch(tree.Branch(name="Branch 1", weight=50, length=120))
        self.assertListEqual(self.tree.branches(),["Branch 1", "Branch 1 (1)"])
        self.tree.add_branch(tree.Branch(name="Branch 1 (1)", weight=50, length=120))
        self.assertListEqual(self.tree.branches(),["Branch 1", "Branch 1 (1)", "Branch 1 (2)"])

    def test_moving_branch_where_its_name_already_exists_will_make_it_rename(self):
        self.tree.add_branch(tree.Branch(name="Branch 1", weight=25, length=70), "Branch 1")
        self.assertListEqual(self.tree.branches("Branch 1"),["Branch 1"])
        self.tree.move_branch(("Branch 1","Branch 1"),())
        self.assertListEqual(self.tree.branches("Branch 1"),[])
        # The moved branch 'Branch 1' found itself to be moved into location, where 'Branch 1' already existed,
        # thus, it changed its name to 'Branch 1 (1)'
        self.assertListEqual(self.tree.branches(), ["Branch 1", "Branch 1 (1)"])

    def test_renaming_branch_to_name_that_is_not_already_taken_can_be_done(self):
        self.tree.add_branch(tree.Branch(name="Branch 2", weight=25, length=70))
        self.tree.rename_branch(("Branch 2",),"Branch X")
        self.assertListEqual(self.tree.branches(),["Branch 1","Branch X"])     

    def test_renaming_branch_to_name_already_taken_will_make_it_adjust_its_new_name(self):
        self.tree.add_branch(tree.Branch(name="Branch 2", weight=25, length=70))
        self.tree.rename_branch(("Branch 2",),"Branch 1")
        self.assertListEqual(self.tree.branches(),["Branch 1","Branch 1 (1)"])


if __name__=="__main__": unittest.main()