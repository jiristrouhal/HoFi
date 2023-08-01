import sys 
sys.path.insert(1,"src")

import app
import unittest


class Test_Nothing(unittest.TestCase):

    def test_nothing(self):
        self.assertTrue(True)


