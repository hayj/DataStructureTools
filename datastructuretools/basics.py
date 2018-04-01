# coding: utf-8

from collections import OrderedDict

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


if __name__ == '__main__':
    pass






