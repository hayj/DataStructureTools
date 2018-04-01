# coding: utf-8
# pew in datastructuretools-venv python ./test/setqueue.py

import os
import sys
sys.path.append('../')

import unittest
import doctest
from datastructuretools import setqueue
from datastructuretools.setqueue import *

# The level allow the unit test execution to choose only the top level test 
min = 0
max = 1
assert min <= max

print("==============\nStarting unit tests...")

if min <= 0 <= max:
    class DocTest(unittest.TestCase):
        def testDoctests(self):
            """Run doctests"""
            doctest.testmod(setqueue)

if min <= 1 <= max:
    class Test1(unittest.TestCase):
        def test1(self):
            print("Starting test1...")
            q = OrderedSetQueue(3)
            q.put(1)
            q.put(1)
            q.put(1)
            q.get()
            q.put(2)
            q.put(2)
            q.put(3)
            q.put(4)
            self.assertTrue(1 not in q)
            self.assertTrue(3 in q)
            self.assertTrue(4 in q)
            self.assertTrue(q.size() == 3)
            self.assertTrue(q.get() == 2)
            self.assertTrue(q.get() == 3)
            self.assertTrue(q.get() == 4)
            print("test1 done.")

        def test2(self):
            print("Starting test2...")
            q = OrderedSetQueue(3)
            q.put(1)
            q.put(1)
            q.put(1)
            q.get()
            q.put(2)
            q.put(2)
            q.put(3)
            q.put(4)
            q.get()
            q2 = cloneQueue(q)
            q.get()
            self.assertTrue(2 not in q2)
            self.assertTrue(3 in q2)
            self.assertTrue(4 in q2)
            self.assertTrue(q.size() == 1)
            self.assertTrue(q2.size() == 2)
            self.assertTrue(q2.get() == 3)
            print("test2 done.")

        def test3(self):
            print("Starting test3...")
            q = OrderedSetQueue(3)
            q.put(1)
            q.put(1)
            q.put(1)
            q.get()
            q.put(2)
            q.put(2)
            q.put(3)
            q.put(4)
            q.get()
            q2 = cloneQueue(q)
            q.get()
            l = queueToList(q2)
            q2 = listToQueue(l)
            self.assertTrue(2 not in q2)
            self.assertTrue(3 in q2)
            self.assertTrue(4 in q2)
            self.assertTrue(q.size() == 1)
            self.assertTrue(q2.size() == 2)
            self.assertTrue(q2.get() == 3)
            print("test3 done.")

if __name__ == '__main__':
    unittest.main() # Or execute as Python unit-test in eclipse


print("Unit tests done.\n==============")