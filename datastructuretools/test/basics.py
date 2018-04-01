


# coding: utf-8
# pew in datatools-venv python ./test/basics.py

import os
import sys
sys.path.append('../')

import unittest
import doctest
import time
from systemtools.basics import *
from systemtools.location import *
from systemtools.file import *
from datastructuretools import basics
from datastructuretools.basics import *

# The level allow the unit test execution to choose only the top level test
min = 1
max = 1
assert min <= max

print("==============\nStarting unit tests...")

if min <= 0 <= max:
    class DocTest(unittest.TestCase):
        def testDoctests(self):
            """Run doctests"""
            doctest.testmod(basics)

if min <= 1 <= max:
    class Test1(unittest.TestCase):
        def test1(self):
            def funct(key):
                return key + 10
            cd = CacheDict(funct, 3)
            self.assertTrue(len(cd) == 0)
            self.assertTrue(cd[1] == 11)
            self.assertTrue(cd[1] == 11)
            print(cd[1])
            self.assertTrue(len(cd) == 1)
            self.assertTrue(cd[2] == 12)
            self.assertTrue(len(cd) == 2)
            self.assertTrue(cd[3] == 13)
            self.assertTrue(len(cd) == 3)
            self.assertTrue(cd[4] == 14)
            self.assertTrue(len(cd) == 3)
            self.assertTrue(1 not in cd)
            self.assertTrue(2 in cd)
            print(len(cd))




if __name__ == '__main__':
    unittest.main() # Or execute as Python unit-test in eclipse
    print("Unit tests done.\n==============")


