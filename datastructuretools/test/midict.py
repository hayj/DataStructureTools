# coding: utf-8
# pew in systemtools-venv python ./test/basics.py

import os
import sys

import unittest
import doctest
from systemtools.printer import *
from datastructuretools import midict
from datastructuretools.midict import *

# The level allow the unit test execution to choose only the top level test
mini = 0
maxi = 15
assert mini <= maxi

print("==============\nStarting unit tests...")

if mini <= 0 <= maxi:
    class DocTest(unittest.TestCase):
        def testDoctests(self):
            """Run doctests"""
            doctest.testmod(midict)

if mini <= 1 <= maxi:
    class Test1(unittest.TestCase):
        def test1(self):
            gotException = False
            try:
                d = MIDict(['a'])
            except:
                gotException = True
            self.assertTrue(gotException)

            gotException = False
            try:
                d = MIDict([('a',)])
            except:
                gotException = True
            self.assertTrue(gotException)

            gotException = False
            try:
                d = MIDict([('a', None)])
            except:
                gotException = True
            self.assertTrue(not gotException)

            gotException = False
            try:
                d = MIDict([('a', None), (None, 1)])
            except:
                gotException = True
            self.assertTrue(not gotException)

            self.assertTrue(len(d) == 2)
            self.assertTrue(d[None][0] == 1)

        def test2(self):
            d = MIDict([('a', None), (None, 1)])
            self.assertTrue(d.items() == [('a', None), (None, 1)])
            d = MIDict()
            d['a'] = None
            d[None] = 1
            self.assertTrue(set(d.items()) == set([('a', None), (None, 1)]))

        def test3(self):
            d = MIDict()
            d[20,60]
            d[20,80]
            d[20,100]
            d[20,100]
            d[30,100]
            self.assertTrue(len(d) == 4)
            self.assertTrue(len(d[:,100]) == 2)

        def test4(self):
            d = MIDict()
            d[20,60,100]
            d[20,60,200]
            self.assertTrue(len(d) == 2)
            
            gotException = False
            try:
                d[20,60,200,500]
            except:
                gotException = True
            self.assertTrue(gotException)

            gotException = False
            try:
                d[20,60,200] = 1
            except Exception as e:
                gotException = True
            self.assertTrue(gotException)

            gotException = False
            try:
                d[20] = 1
            except:
                gotException = True
            self.assertTrue(gotException)

            d[30] = (20, 40)
            self.assertTrue(len(d) == 3)
            self.assertTrue(d[30][0] == (20, 40))
            self.assertTrue(d[:,20][0] == (30, 40))
            self.assertTrue(d[:,:,100][0] == (20, 60))
            self.assertTrue(d[:,60,:] == [(20, 100), (20, 200)])


        def test5(self):
            d = MIDict()
            d[20,60,100]
            d[20,60,200]
            
            self.assertTrue(d[20,:,100][0] == 60)
            d[20,:,100] = 4
            self.assertTrue(d[20,:,100][0] == 4)
            self.assertTrue(len(d) == 2)

            d[20,100] = 4
            self.assertTrue(len(d) == 3)
            self.assertTrue(d[20,100][0] == 4)

        def test5_2(self):
            d = MIDict()
            d[1,2] = 4
            self.assertTrue(len(d) == 1)
            self.assertTrue(d.items() == [(1,2,4)])

        def test5_3(self):
            d = MIDict()
            d[1,:,:] = (2, 4)
            self.assertTrue(len(d) == 1)
            self.assertTrue(d.items() == [(1,2,4)])

        def test5_4(self):
            d = MIDict()
            d[1,:,4] = 2
            self.assertTrue(len(d) == 1)
            self.assertTrue(d.items() == [(1,2,4)])
            d[1,2] = 4
            self.assertTrue(len(d) == 1)
            self.assertTrue(d.items() == [(1,2,4)])
            d[1,1] = 4
            self.assertTrue(len(d) == 2)
            self.assertTrue(set(d.items()) == {(1,2,4), (1,1,4)})




        def test6(self):
            d = MIDict()
            d[1,:,:] = (2, 4)
            d[10, 20, 30]
            d[100, 200, 30]
            self.assertTrue(len(d) == 3)
            d[:,:,30] = (None, None)
            self.assertTrue(len(d) == 2)
            self.assertTrue(set(d.items()) == {(1,2,4), (None,None,30)})

        def test7(self):
            d = MIDict()
            d[1,:,:] = (2, 4)
            d[10, 20, 30]
            d[100, 200, 300]
            self.assertTrue(len(d) == 3)
            d[:,:,30] = (None, None)
            self.assertTrue(len(d) == 3)
            self.assertTrue(set(d.items()) == {(1,2,4), (None,None,30), (100, 200, 300)})

        def test8(self):
            d = MIDict()
            d[1,:,:] = (2, 4)
            d[:,2,5] = 1
            self.assertTrue(len(d) == 2)
            d[1,2] = 6
            self.assertTrue(len(d) == 1)
            self.assertTrue(set(d.items()) == {(1,2,6)})
            d[1,3] = 6

            gotException = False
            try:
                d[1,:] = 6
            except:
                gotException = True
            self.assertTrue(gotException)

            d[1,:,:] = (6, 10)
            self.assertTrue(len(d) == 1)
            self.assertTrue(set(d.items()) == {(1,6,10)})
            d[2,6,10]
            d[2,10,10]
            self.assertTrue(len(d) == 3)
            d.verbose = True
            d[:,:,:] = (2,10,10)
            self.assertTrue(len(d) == 1)
            self.assertTrue(set(d.items()) == {(2,10,10)})

            del d[:,:,:]
            self.assertTrue(len(d) == 0)
            d[:,:,:] = (2,10,10)
            d[2,6,10]
            d[2,6] = 11
            del d[:,:,11]
            self.assertTrue(len(d) == 1)

        def test9(self):
            d = MIDict()
            d[:,:,1] = (4, 5)
            self.assertTrue(len(d) == 1)
            self.assertTrue(set(d.items()) == {(4,5,1)})
            d[:,:,1] = (6, 8)
            self.assertTrue(len(d) == 1)
            self.assertTrue(set(d.items()) == {(6,8,1)})
            d[6,:,1] = 8
            self.assertTrue(len(d) == 1)
            self.assertTrue(set(d.items()) == {(6,8,1)})
            d[6,8] = 1
            self.assertTrue(len(d) == 1)
            d[6,9] = 1
            self.assertTrue(len(d) == 2)
            self.assertTrue(len(d[:,:,1]) == 2)
            d[10,5,1]
            self.assertTrue(len(d) == 3)
            d[3,4,1]
            d[:,:,1] = (3, 4)
            self.assertTrue(len(d) == 1)
            del d[:,4,:]
            self.assertTrue(len(d) == 0)
            d[3,4,1]
            self.assertTrue(len(d) == 1)

if __name__ == '__main__':
    unittest.main() # Orb execute as Python unit-test in eclipse


print("Unit tests done.\n==============")