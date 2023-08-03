import sys 
sys.path.insert(1,"src")


import treeview
import unittest


class Test_Nothing(unittest.TestCase):

    def test_nothing(self): 
        self.assertTrue(True)


if __name__=="__main__": unittest.main()