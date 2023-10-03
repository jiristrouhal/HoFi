from __future__ import annotations
import sys 
sys.path.insert(1,"src")


import unittest
from src.core.editor import new_editor


class Test_Create_New_Case(unittest.TestCase):

    def test_create_new_case(self):
        editor = new_editor()
        newcase = editor.new('Case')


if __name__=="__main__": unittest.main()

