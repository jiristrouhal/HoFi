import sys 
sys.path.insert(1,'src')

import unittest
import src.app


class Test_Saving_Tree(unittest.TestCase):

    def test_nothing(self):
        self.assertTrue(True)


if __name__=="__main__": unittest.main()