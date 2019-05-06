# coding: utf-8

from collections import OrderedDict
from systemtools.logger import *
from systemtools.duration import *
from systemtools.location import *
from systemtools.file import *
import shutil

class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

def hashableDictListToDictList(hashableDictList):
    results = []
    for current in hashableDictList:
        results.append(hashableDictToDict(current))
    return results

def hashableDictToDict(hashableDict):
    result = dict()
    for key, value in hashableDict.items():
        result[key] = value
    return result

class CacheDict(OrderedDict):
    """
        This struct is initialized with a size limit
        and a funct which process each key
        the __getitem__ will process the key if it
        doesn't exists, else it return the value
        corresponding to the key
        https://stackoverflow.com/questions/2437617/limiting-the-size-of-a-python-dictionary
    """
    def __init__(self, funct, limit=0):
        self.size_limit = limit
        self.funct = funct
#         self.size_limit = kwds.pop("limit", None)
#         self.funct = kwds.pop("funct", None)
#         OrderedDict.__init__(self, *args, **kwds)
        OrderedDict.__init__(self)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def superGet(self, key):
        return super(CacheDict, self).__getitem__(key)

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)
    def __getitem__(self, key):
        if key not in self:
            value = self.funct(key)
            self[key] = value
            return value
        else:
            return self.superGet(key)


class ListChunker:
    """
        This class take an iterable and serialize it on disk in different
        files according to the given chunks size.
    """
    def __init__(self, chunksSize, iterable=None, dirPath=None, logger=None, verbose=True, itemizeDict=True):
        self.chunksSize = chunksSize
        self.logger = logger
        self.verbose = verbose
        self.filesPath = []
        self.currentList = []
        self.totalSize = 0
        self.dirPath = dirPath
        if self.dirPath is None:
            self.dirPath = tmpDir("listchunker") + "/" + getRandomStr()
        mkdir(self.dirPath)
        if iterable is not None:
            if itemizeDict and isinstance(iterable, dict):
                iterable = iterable.items()
            for current in iterable:
                self.append(current)
            self.close()

    def __serialize(self):
        if len(self.currentList) > 0:
            filePath = self.dirPath + "/" + str(len(self.filesPath)) + ".pickle"
            serialize(self.currentList, filePath)
            self.currentList = []
            self.filesPath.append(filePath)

    def close(self):
        self.__serialize()

    def append(self, element):
        self.currentList.append(element)
        self.totalSize += 1
        if len(self.currentList) == self.chunksSize:
            self.__serialize()

    def __len__(self):
        length = len(self.filesPath)
        if len(self.currentList) > 0:
            length += 1
        return length

    def __getitem__(self, index):
        if len(self.currentList) > 0 and index == len(self.filesPath):
            return self.currentList
        elif index >= 0 and index < len(self.filesPath):
            return deserialize(self.filesPath[index])
        else:
            raise IndexError()

    def reset(self):
        self.filesPath = []
        self.currentList = []
        removeDirSecure(self.dirPath)

    def getTotalSize(self):
        return self.totalSize

    def copyFiles(self, dirPath):
        self.close()
        if len(self.filesPath) > 6:
            verbose = self.verbose
        else:
            verbose = False
        for current in pb(self.filesPath, logger=self.logger, verbose=verbose, message="Storing current chunks to " + dirPath):
            shutil.copyfile(current, dirPath + "/" + decomposePath(current)[3])

def deserializeListChunks(dirPath, unItemizeDict=False, logger=None, verbose=True):
    if unItemizeDict:
        data = dict()
    else:
        data = []    
    for path in pb(sortedGlob(dirPath + "/*.pickle"), logger=logger, verbose=verbose):
        current = deserialize(path)
        if unItemizeDict:
            for key, value in current:
                data[key] = value
        else:
            data += current
    return data

if __name__ == '__main__':
    elements = list(range(840))
    lc = ListChunker(100, elements)

    print(len(lc))
    # print(len(lc[7]))
    # print(lc[7])

    for current in lc:
        print(current)

    print(lc.getTotalSize())

    if isinstance(lc, list):
        print("list")

    if isinstance(lc, ListChunker):
        print("aaaaaaa")


    lc.copyFiles(tmpDir("listchunker-copy-test"))

    lc.reset()







