from systemtools.printer import *
from systemtools.logger import *

class MIDict:
    def __init__(self, initial=None, logger=None, verbose=False):
        """
            The MIdict (Multi-indexed dictionary) data structure is a basic python dict that simultaneously index the key and the value. Thus you can get a key given its value. The access to a row in the datastructure always returns a list because a value can correspond to multiple rows. The data structure can index an amount of values greater than 2. Thus each element of a row is called a value. The first element, called a key in a classical python dict, is also a value. Values are not necessary unique (even the first) but whole rows are unique. Thus the datastrure bring a compound index on each columns that are not unique. See example below to see the usage of MIDict.
        """
        # data is a list of tuples
        # each tuple takes a dict and another dict
        # the first dict map objects the user give to each rows where we can find it (so a set)
        # the second is a dict that map a row index to its object
        self.logger = logger
        self.verbose = verbose
        self.data = None
        self.newRowIndex = 0
        if initial is not None:
            if not isinstance(initial, list):
                raise Exception("Initial data must be a list")
            for current in initial:
                self[current]
    
    def __initData(self, width):
        if self.data is None:
            if width < 2:
                raise Exception("The number of columns must be greater or equals to 2.")
            self.data = []
            for i in range(width):
                self.data.append((dict(), dict()))

    def __normalize(self, keys):
        self.__initData(len(keys))
        query = dict()
        for i in range(len(keys)):
            if not isinstance(keys[i], slice):
                query[i] = keys[i]
        if len(query) > len(self.data):
            raise Exception("You cannot specify more keys / values than specified when you called the first time `__setitem__` or `__getitem__`.")
        return query
    
    def __alreadyExists(self, query):
        if len(query) < len(self.data):
            return False
        else:
            alreadyExists = True
            try:
                inter = None
                for index, value in query.items():
                    if inter is None:
                        inter = set(self.data[index][0][value])
                    else:
                        inter = inter.intersection(self.data[index][0][value])
                assert len(inter) == 1
            except: alreadyExists = False
            return alreadyExists
    
    def __rowExists(self, row):
        for col in range(len(self.data)):
            if row not in self.data[col][1]:
                return False
        return True
    
    def __getitem__(self, keys):
        if not isinstance(keys, tuple):
            keys = (keys,)
        query = self.__normalize(keys)
        # In case it's a set:
        if len(query) == len(self.data):
            # First we check if the row already exists:
            alreadyExists = self.__alreadyExists(query)
            # If not, we add it:
            if not alreadyExists:
                rowIndex = self.newRowIndex
                self.newRowIndex += 1
                for index, value in query.items():
                    if value not in self.data[index][0]:
                        self.data[index][0][value] = set()
                    self.data[index][0][value].add(rowIndex)
                    self.data[index][1][rowIndex] = value
            # And finally we return the same values:
            return [keys]
        # Else if the query is empty, we return all:
        elif len(query) == 0:
            results = []
            for row in range(self.newRowIndex):
                if self.__rowExists(row):
                    result = []
                    for col in range(len(self.data)):
                        result.append(self.data[col][1][row])
                    results.append(tuple(result))
            return results
        # Else in case it's a get:
        else:
            # We search all rows that match:
            inter = None
            try:
                for index, value in query.items():
                    if inter is None:
                        inter = set(self.data[index][0][value])
                    else:
                        inter = inter.intersection(self.data[index][0][value])
                assert len(inter) > 0
            except: return []
            # We append all:
            results = []
            for row in inter:
                result = []
                for col in range(len(self.data)):
                    if col not in query:
                        result.append(self.data[col][1][row])
                if len(result) == 1:
                    result = result[0]
                else:
                    result = tuple(result)
                results.append(result)
            return results

    def __setitem__(self, keys, values):
        if isinstance(values, tuple) and len(values) == 0:
            raise Exception("Cannot set nothing")
        if not isinstance(keys, tuple):
            keys = (keys,)
        if not isinstance(values, tuple):
            values = (values,)
        self.__initData(len([e for e in keys if not isinstance(e, slice)]) + len(values))
        query = self.__normalize(keys)
        # log(b(query), self)
        if len(self.data) != len(query) + len(values):
            raise Exception("Wrong shape, expected " + str(len(self.data)) + " but got " + str(len(query) + len(values)) + " elements")
        # log(b(keys), self)
        # log(b(self.data), self)
        del self[keys]
        # log(b(self.data), self)
        newKeys = []
        values = list(values)
        keys = list(keys)
        for i in range(len(self.data)):
            if i in query:
                newKeys.append(keys[0])
                keys = keys[1:]
            else:
                newKeys.append(values[0])
                values = values[1:]
                keys = keys[1:]
        newKeys = tuple(newKeys)
        self[newKeys]
    
    def __delitem__(self, keys):
        query = self.__normalize(keys)
        onlySlices = True
        for current in keys:
            if not isinstance(current, slice):
                onlySlices = False
        if onlySlices:
            self.data = None
            self.__initData(len(keys))
        # We search all rows that match:
        try:
            inter = None
            for index, value in query.items():
                if inter is None:
                    inter = set(self.data[index][0][value])
                else:
                    inter = inter.intersection(self.data[index][0][value])
            assert len(inter) > 0
        except: inter = None
        if inter is not None:
            for row in inter:
                for col in range(len(self.data)):
                    value = self.data[col][1][row]
                    del self.data[col][1][row]
                    self.data[col][0][value].remove(row)
                    if len(self.data[col][0][value]) == 0:
                        del self.data[col][0][value]
    
    def items(self):
        return self[:]
    
    def keys(self):
        return self.data[0][0].keys()
    
    def __contains__(self, keys):
        return len(self[keys]) > 0
    
    def __len__(self):
        try:
            return len(self.data[0][1])
        except:
            return False