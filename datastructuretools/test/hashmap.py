


# coding: utf-8
# pew in datastructuretools-venv python ./test/hashmap.py

import os
import sys
sys.path.append('../')

import unittest
import doctest
import time
from systemtools.basics import *
from systemtools.location import *
from systemtools.file import *
from datastructuretools import hashmap
from datastructuretools.hashmap import *

# The level allow the unit test execution to choose only the top level test
min = 0
max = 11
assert min <= max

print("==============\nStarting unit tests...")

if min <= 0 <= max:
    class DocTest(unittest.TestCase):
        def testDoctests(self):
            """Run doctests"""
            doctest.testmod(hashmap)

if min <= 2 <= max:
    class Test2(unittest.TestCase):
        def test1(self):
            for useMongodb in [False, True]:
                dataPath = tmpDir() + "/test.pickle.zip"
                removeIfExists(dataPath)
                sd = SerializableDict("test", tmpDir(),
                                      cleanNotReadOrModifiedSinceNSeconds=2,
                                      serializeEachNAction=50,
                                      cleanEachNAction=110,
                                      useMongodb=useMongodb,)
                for i in range(100):
                    if i == 49:
                        print()
                    randomStr1 = getRandomStr()
                    sd.add(randomStr1, 1)

                self.assertTrue(sd.size() == 100)
                self.assertTrue(sd.hasKey(randomStr1))
                if not useMongodb:
                    self.assertTrue(fileExists(dataPath))
                else:
                    self.assertFalse(fileExists(dataPath))


                time.sleep(3)
                for i in range(20):
                    randomStr = getRandomStr()
                    sd.add(randomStr, 1)

                self.assertTrue(sd.size() == 20)
                self.assertTrue(sd.hasKey(randomStr))
                self.assertTrue(not sd.hasKey(randomStr1))

                sd.close()
                sd.reset()
                self.assertFalse(fileExists(dataPath))


if min <= 3 <= max:
    class Test3(unittest.TestCase):
        def test1(self):
            for useMongodb in [True, False]:
                dataPath = tmpDir() + "/test2.pickle.zip"
                removeIfExists(dataPath)
                sd = SerializableDict("test2", tmpDir(),
                                      limit=10,
                                      serializeEachNAction=200,
                                      cleanEachNAction=200,
                                      verbose=True,
                                      useMongodb=useMongodb,)
                randomStrs = []
                for i in range(20):
                    randomStr1 = getRandomStr()
                    randomStrs.append(randomStr1)
                    sd.add(randomStr1, 1)

                sd.clean()

                for i in range(0, 9):
                    self.assertTrue(not sd.hasKey(randomStrs[i]))

                for i in range(10, 19):
                    self.assertTrue(sd.hasKey(randomStrs[i]))

                self.assertTrue(sd.size() == 10)

                theRandomStr = getRandomStr()
                sd.add(theRandomStr, 2)
                sd.get(randomStrs[10])
                sd.add(randomStrs[11], 2)
                sd.clean()
                self.assertTrue(sd.hasKey(randomStrs[10]))
                self.assertTrue(sd.hasKey(randomStrs[11]))
                self.assertTrue(not sd.hasKey(randomStrs[12]))
                self.assertTrue(sd.hasKey(randomStrs[13]))
                self.assertTrue(sd.hasKey(randomStrs[19]))
                self.assertTrue(sd.hasKey(theRandomStr))
                sd.reset()




if min <= 4 <= max:
    class Test4(unittest.TestCase):
        def test1(self):
            for useMongodb in [False]:
                dataPath = tmpDir() + "/test4.pickle.zip"
                removeIfExists(dataPath)
                sd = SerializableDict("test4", tmpDir(),
                                      cleanMaxSizeMoReadModifiedOlder=30,
                                      serializeEachNAction=1000,
                                      cleanEachNAction=1000,
                                      verbose=True,
                                      useMongodb=useMongodb,)

                gotLowerSizeThanPrevious = False
                gotLowerDataSizeThanPrevious = False
                previousDataSize = -10
                previousSize = -10

                for i in range(100000):
                    if i % 10000 == 0:
                        currentDataSize = sd.dataSizeMo()
                        currentSize = sd.size()
                        if currentSize < previousSize:
                            gotLowerSizeThanPrevious = True
                        if currentDataSize < previousDataSize:
                            gotLowerDataSizeThanPrevious = True
                        if gotLowerDataSizeThanPrevious and gotLowerSizeThanPrevious:
                            break
                        print("i=" + str(i))
                        print("objectSize=" + str(objectSize(sd.data)))
                        print("dataSize=" + str(currentDataSize) + " Mo")
                        print("size=" + str(currentSize))
                        previousSize = currentSize
                        previousDataSize = currentDataSize

    #                     input()
                    sd.add(i, {getRandomStr(): getRandomStr()})

                self.assertTrue(gotLowerDataSizeThanPrevious)
                self.assertTrue(gotLowerSizeThanPrevious)

                sd.reset()

if min <= 5 <= max:
    class Test5(unittest.TestCase):
        def test2(self):
            for useMongodb in [True, False]:
                dataPath = tmpDir() + "/test5.pickle.zip"
                removeIfExists(dataPath)
                sd = SerializableDict("test5", tmpDir(),
                                      limit=10,
                                      serializeEachNAction=200,
                                      cleanEachNAction=200,
                                      verbose=True,
                                      useMongodb=useMongodb,)
                randomStrs = []
                for i in range(20):
                    randomStr1 = getRandomStr()
                    randomStrs.append(randomStr1)
                    sd[randomStr1] = 1

                sd.clean()

                for i in range(0, 9):
                    self.assertTrue(randomStrs[i] not in sd)

                for i in range(10, 19):
                    self.assertTrue(randomStrs[i] in sd)

                self.assertTrue(len(sd) == 10)

                theRandomStr = getRandomStr()
                sd[theRandomStr] = 2
                sd[randomStrs[10]]
                sd[randomStrs[11]] = 2
                sd.clean()
                self.assertTrue(randomStrs[10] in sd)
                self.assertTrue(randomStrs[11] in sd)
                self.assertTrue(randomStrs[12] not in sd)
                self.assertTrue(randomStrs[13] in sd)
                self.assertTrue(randomStrs[19] in sd)
                self.assertTrue(theRandomStr in sd)

                sd.save()
                if not useMongodb:
                    self.assertTrue(fileExists(dataPath))
                sd.reset()
                sd.removeFile()
                self.assertTrue(not fileExists(dataPath))

if min <= 6 <= max:
    class Test6(unittest.TestCase):
        def test2(self):
            for useMongodb in [True, False]:
                dataPath = tmpDir() + "/test6.pickle.zip"
                removeIfExists(dataPath)
                def processingFunct(key):
                    return str(key) + "aaa"
                sd = SerializableDict("test6", tmpDir(),
                                      limit=3,
                                      serializeEachNAction=2,
                                      cleanEachNAction=2,
                                      verbose=True,
                                      funct=processingFunct,
                                      useMongodb=useMongodb,)

                self.assertTrue(not fileExists(dataPath))
                self.assertTrue(sd[1] == "1aaa")
                self.assertTrue(sd[2] == "2aaa")
                self.assertTrue(sd[2] == "2aaa")
                self.assertTrue(len(sd) == 2)
                self.assertTrue(sd[2] == "2aaa")
                self.assertTrue(sd[3] == "3aaa")
                self.assertTrue(len(sd) == 3)
                self.assertTrue(3 in sd)
                self.assertTrue(sd[4] == "4aaa")
                self.assertTrue(4 in sd)
                self.assertTrue(1 not in sd)
                if not useMongodb:
                    self.assertTrue(fileExists(dataPath))
                sd.reset()
                sd.removeFile()
                self.assertTrue(not fileExists(dataPath))

if min <= 8 <= max:
    class Test8(unittest.TestCase):
        def test1(self):
            for useMongodb in [True, False]:
                def somethingFunct():
                    return "something"
                def processing1(key, something=None):
                    if something is None:
                        something = ""
                    else:
                        something = something()
                    return key + "_a_" + something
                def processing2(key, something=None):
                    if something is None:
                        something = ""
                    else:
                        something = something()
                    return key + "_b_" + something

                sd = SerializableDict("Test8", limit=3,
                          cleanEachNAction=2000,
                          verbose=True,
                          funct=processing1,
                          cacheCheckRatio=0.5,
                          useMongodb=useMongodb,)


                self.assertTrue(sd["u"] == "u_a_")
                value = sd.get("u")
                self.assertTrue(not isFile(sd.filePath))
                self.assertTrue(value == "u_a_")
                isException = False
                try:
                    for i in range(2000):
                        value = sd.get("u", something=somethingFunct)
                except:
                    isException = True
                self.assertTrue(isException)

                self.assertTrue(len(sd) == 1)
                del sd["u"]
                self.assertTrue(len(sd) == 0)
                isException = False
                try:
                    for i in range(2000):
                        value = sd.get("u", something=somethingFunct)
                except:
                    isException = True
                self.assertTrue(not isException)
                self.assertTrue(sd.get("u", something=somethingFunct) == "u_a_something")



                sd.processingFunct = processing2
                isException = False
                try:
                    for i in range(2000):
                        value = sd.get("u", something=somethingFunct)
                except:
                    isException = True
                self.assertTrue(isException)



                print(sd.filePath)
                if not useMongodb:
                    self.assertTrue(isFile(sd.filePath))
                sd.serialize()
                if not useMongodb:
                    self.assertTrue(isFile(sd.filePath))
                sd.removeFile()
                self.assertTrue(not isFile(sd.filePath))

                sd.reset()



if min <= 9 <= max:
    class Test9(unittest.TestCase):
        def test1(self):
            for useMongodb in [False]:
                def getValues(key):
                    return ([[]], "a")
                print("test9")
                sd = SerializableDict("test9", tmpDir(), funct=getValues,
                              cacheCheckRatio=0.0, limit=100,
                              serializeEachNAction=1, compresslevel=0,
                                useMongodb=useMongodb,)
                sd["a"]
                self.assertTrue(isFile(sd.filePath))
                sd.reset()
                self.assertTrue(not isFile(sd.filePath))

if min <= 10 <= max:
    class Test10(unittest.TestCase):
        def test1(self):
            for useMongodb in [True]:
                def fucnt1(key):
                    return "a.a.a" + str(key)
                print("MONGO TEST")
                sd = SerializableDict("Test10", funct=fucnt1, limit=100,
                                useMongodb=useMongodb, cleanEachNAction=2)
                sd["a"]
                sd["b"]
                sd["c"]
                sd["d"]
                for i in range(98):
                    sd[getRandomFloat(decimalMax=20)]
                self.assertTrue("a" not in sd)
                self.assertTrue("d" in sd)
                self.assertTrue(len(sd["d"]) > 4)
                print(sd["d"])
                self.assertTrue(sd["d"].startswith("a.a.a"))


                sd.reset()
if min <= 11 <= max:
    class Test11(unittest.TestCase):
        def test1(self):
            for useMongodb in [True, False]:
                print("TEST11")
                sd = SerializableDict("Test11", limit=100,
                                useMongodb=useMongodb, cleanEachNAction=100)
                sd.reset()
                sd["a"] = 1
                sd["b"] = 1
                sd["c"] = 1
                sd["a"] += 1
                sd["a"] += 1
                sd["a"] += 1
                self.assertTrue(sd["a"] == 4)
                self.assertTrue(sd["b"] == 1)
                sd.reset()




if __name__ == '__main__':
    unittest.main() # Or execute as Python unit-test in eclipse


    print("Unit tests done.\n==============")













# if min <= 1 <= max:
#     # DEPRECATED
#     class Test1(unittest.TestCase):
#         def setUp(self):
#             pass
#
#         def testLoadingAll(self):
#
#             workingDirectory = getWorkingDirectory() + "/test_limitedhashmap.bin";
#             hm = SerializableHashMap(workingDirectory);
#             hm.clean();
#
#             self.assertTrue(hm.getOne("test1") == None);
#             self.assertTrue(hm.getOne("468748641") == None);
#
#             hm.add("test1", 15);
#             hm.add("test2", "yo");
#
#             self.assertTrue(hm.getOne("test2") is not None);
#
#             hm.serialize();
#
#             hm.getOne("test1");
#
#             hm2 = SerializableHashMap(workingDirectory);
#
#             self.assertTrue(hm.getOne("test2") == hm2.getOne("test2"));
#
#
#         def testTryAgain(self):
#             # to test the clean...
#             self.testLoadingAll();
#
#
#         def testRecursive(self):
#
#             workingDirectory = getWorkingDirectory() + "/test2_limitedhashmap.bin";
#             hm = SerializableHashMap(workingDirectory);
#             hm.clean();
#
#             d = dict();
#             d2 = dict();
#             d2["test"] = 42;
#             d["d2"] = d2;
#             hm.add("d", d);
#             hm.serialize();
#
#
#             hm2 = SerializableHashMap(workingDirectory);
#             self.assertTrue(hm2.getOne("d")["d2"]["test"] == d2["test"]);
#
#
#         def testSentencePair(self):
#             d = dict();
#             obj = SentencePair('a', 'b');
#             d[obj] = "yo"
#             self.assertTrue(d[obj] == 'yo');
#             self.assertTrue(SentencePair('a', 'b') in d);
#             self.assertTrue(d[SentencePair('a', 'b')] == "yo");
#             self.assertTrue((SentencePair('c', 'd') in d) == False);
