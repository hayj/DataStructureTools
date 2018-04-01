# coding: utf-8

import pickle as pickle
from datastructuretools.hashmap import *


def getValues(key):
    return getRandomFloat()
sd = SerializableDict("test9", "/home/hayj", funct=getValues,
              cacheCheckRatio=0.0, limit=100,
              serializeEachNAction=1, compresslevel=0)
for i in range(1000):
    sd[i]

f = open("/home/hayj/pickletest.pickle.zip", 'wb')

data = {1: "a", 2: "b"}
print("a")
pickle.dump(sd.data, f, pickle.HIGHEST_PROTOCOL)
print("b")

f.close()
print("c")
