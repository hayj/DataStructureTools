# coding: utf-8

import pickle as pickle
from systemtools.basics import *
from systemtools.logger import *
from systemtools.location import *
from systemtools.file import *
from databasetools.mongo import *
from datastructuretools import config
import os
import gzip
import sys
import copy

def objectSizeMo(obj):
    size = sys.getsizeof(obj)
    size /= 1024.0
    size /= 1024.0
    return size

class SerializableDict():
    def __init__ \
    (
        self,
        name=None,
        dirPath=None,
        funct=None,
        compresslevel=0,
        logger=None,
        verbose=False,
        readAndAddOnly=False,
        limit=None,
        cleanMaxSizeMoReadModifiedOlder=None,
        cleanNotReadOrModifiedSinceNDays=None,
        cleanNotReadOrModifiedSinceNSeconds=None,
        cleanEachNAction=500,
        serializeEachNAction=500,
        doSerialize=None,
        cacheCheckRatio=0.0, # 0.01
        raiseBadDesignException=True,
        useMongodb=False,
        host=None, user=None, password=None,
        mongoIndex="hash",
        useLocalhostIfRemoteUnreachable=True,
        mongoDbName=None,
    ):
        """
            Read the README
        """
        # Some checks:
        if dirPath is None:
            dirPath = tmpDir("SerializableDicts")
        if useMongodb:
            doSerialize = False
        if doSerialize is None:
            if name is None:
                doSerialize = False
            else:
                doSerialize = True
        if name is None and useMongodb:
            raise Exception("Pls set a name for mongodb usage")
        self.name = name
        if self.name is None:
            self.name = getRandomStr()
        self.doSerialize = doSerialize
        self.mongoDbName = mongoDbName
        self.serializeEachNAction = serializeEachNAction
        if not self.doSerialize:
            self.serializeEachNAction = 0
        self.useMongodb = useMongodb
        self.filePath = dirPath + "/" + self.name + ".pickle.zip"

        # Now we store all vars:
        self.useLocalhostIfRemoteUnreachable = useLocalhostIfRemoteUnreachable
        self.mongoIndex = mongoIndex
        self.host = host
        self.user = user
        self.password = password
        self.logger = logger
        self.verbose = verbose
        # Config:
        if self.user is None:
            self.user = config.sdUser
        if self.password is None:
            self.password = config.sdPassword
        if self.host is None:
            self.host = config.sdHost
        if self.mongoDbName is None:
            self.mongoDbName = config.sdDatabaseName
        self.cleanMaxSizeMoReadModifiedOlder = cleanMaxSizeMoReadModifiedOlder
        self.initData()
        self.processingFunct = funct
        self.raiseBadDesignException = raiseBadDesignException
        self.cacheCheckRatio = cacheCheckRatio
        self.readAndAddOnly = readAndAddOnly
        self.actionCount = 0
        self.cleanEachNAction = cleanEachNAction
        self.cleanMaxValueCountReadModifiedOlder = limit
        self.cleanNotReadOrModifiedSinceNSeconds = cleanNotReadOrModifiedSinceNSeconds
        if self.cleanNotReadOrModifiedSinceNSeconds is None and cleanNotReadOrModifiedSinceNDays is not None:
            self.cleanNotReadOrModifiedSinceNSeconds = cleanNotReadOrModifiedSinceNDays * 3600 * 24
        self.compresslevel = compresslevel
        self.load()
        self.clean()

    def getMongoIndex(self):
        return self.mongoIndex

    def __getitem__(self, index):
        return self.get(index)
    def __setitem__(self, index, value):
        self.add(index, value)
    def __delitem__(self, key):
        if self.hasKey(key):
            del self.data[key]
        self.gotAnAction()
    def __contains__(self, key):
        return self.hasKey(key)
    def __len__(self):
        return self.size()

    def __del__(self):
        """
            Warning: this function is called at the end of the python execution
            So you we can not use it to reset the file et data
        """
        pass
#         return self.stop()


    def items(self):
        for key, value in self.data.items():
            yield (key, value["value"])

    def save(self, *argv, **kwargs):
        self.serialize(*argv, **kwargs)
    def serialize(self):
        if not self.useMongodb:
            f = None
            if self.compresslevel > 0:
                f = gzip.GzipFile(self.filePath, 'wb', compresslevel=self.compresslevel)
            else:
                f = open(self.filePath, 'wb')
            try:
                data = self.data
                # data = copy.deepcopy(self.data)
                # data = dictToMongoStorable\
                # (
                #     data,
                #     logger=self.logger,
                #     verbose=self.verbose,
                #     normalizeKeys=False,
                #     normalizeEnums=False,
                #     normalizeBigInts=False,
                #     convertTuples=False,
                #     convertSets=False,
                # )
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                logException(e, self, location="SerializableDict serialize()")
            finally:
                f.close()


    def add(self, key, value):
        if self.hasKey(key):
            if not self.readAndAddOnly:
                self.updateField(key, "modified", time.time())
                self.updateField(key, "modifiedCount", self.getFieldValue(key, "modifiedCount") + 1)
                self.updateField(key, "value", value)
        else:
            value = {"value": value}
            value["modified"] = time.time()
            value["modifiedCount"] = 0
            value["created"] = time.time()
            value["read"] = time.time()
            value["readCount"] = 0
            if self.useMongodb:
                value[self.mongoIndex] = key
                self.data.insert(value)
            else:
                self.data[key] = value
        self.gotAnAction()

    def conditionalSerialize(self):
        if self.serializeEachNAction is not None and self.serializeEachNAction > 0:
            if self.actionCount % self.serializeEachNAction == 0:
                self.serialize()

    def gotAnAction(self):
        self.actionCount += 1
        self.conditionalSerialize()
        self.conditionalClean()

    def updateRow(self, key, field, value):
        """
            This method update a field of a specific row without
            setting any timestamp in term of read or write.
        """
        if self.useMongodb:
            field = "value." + field
            value = dictToMongoStorable(value)
            self.data.updateOne({self.mongoIndex: key}, {"$set": {field: value}})
        else:
            self.data[key]["value"][field] = value

    def updateField(self, key, field, value):
        """
            Private method, enable an update of the root architecture a the SerializableDict
        """
        if self.useMongodb:
            value = dictToMongoStorable(value)
            self.data.updateOne({self.mongoIndex: key}, {"$set": {field: value}})
        else:
            self.data[key][field] = value

    def getFieldValue(self, key, field):
        if self.useMongodb:
            return self.data.findOne({self.mongoIndex: key})[field]
        else:
            return self.data[key][field]


    def get(self, key, *args, **kwargs):
        if self.hasKey(key):
            self.updateField(key, "read", time.time())
            self.updateField(key, "readCount", self.getFieldValue(key, "readCount") + 1)
            value = self.getFieldValue(key, "value")
            if self.processingFunct is not None and self.cacheCheckRatio > 0.0 and getRandomFloat() < self.cacheCheckRatio:
                valueToCheck = self.processingFunct(key, *args, **kwargs)
                if valueToCheck != value:
                    message = "Bad design of the cache mechanism. The value returned (already present in the cache) is different from the value returned by processingFunct(). WARNING extra datas *args, **kwargs are not taken into account in the indexing mecanism... Also you have to implement an equals function if the object is a complex object."
                    message += "\n\nAlready stored value:\n"
                    message += listToStr(value)
                    message += "\n\nNew value:\n"
                    message += listToStr(valueToCheck)
                    logError(message, self)
                    if isinstance(value, dict):
                        for k1, v1 in value.items():
                            v2 = valueToCheck[k1]
                            if v1 != v2:
                                logError("\n\nOne difference found in:\n", self)
                                logError(listToStr(v1), self)
                                logError(listToStr(v2), self)
                    if self.raiseBadDesignException:
                        raise Exception(message)
            self.gotAnAction()
            return value
        elif self.processingFunct is not None:
            self.add(key, self.processingFunct(key, *args, **kwargs))
            self.gotAnAction()
            return self.get(key, *args, **kwargs)
        else:
            self.gotAnAction()
            return None

    def has(self, *args, **kwargs):
        return self.hasKey(*args, **kwargs)
    def hasKey(self, key):
        if self.useMongodb:
            return self.data.has(key)
        else:
            return key in self.data

    def load(self):
        if not self.useMongodb:
            if self.doSerialize and (len(sortedGlob(self.filePath)) > 0):
                log("Loading " + self.filePath + " from the disk", self)
                f = None
                if self.compresslevel > 0:
                    f = gzip.GzipFile(self.filePath, 'rb', compresslevel=self.compresslevel)
                else:
                    f = open(self.filePath, 'rb')
                try:
                    self.data = pickle.load(f)
                except Exception as e:
                    logException(e, self, location="SerializableDict load")
                finally:
                    f.close()

    def close(self):
        self.clean()
        self.serialize()

    def removeFile(self):
        removeIfExists(self.filePath)

    def initData(self, alreadyRetried=False):
        if self.useMongodb:
            try:
                self.data = MongoCollection\
                (
                    self.mongoDbName,
                    self.name,
                    giveTimestamp=False,
                    indexOn=self.mongoIndex,
                    host=self.host, user=self.user, password=self.password,
                    logger=self.logger,
                    verbose=self.verbose,
                )
            except Exception as e:
                if self.useLocalhostIfRemoteUnreachable and not alreadyRetried:
                    logException(e, self, location="initData hashmap", message="WARNING: we can't access the remote SD, so we use the localhost...")
                    self.user = None
                    self.password = None
                    self.host = "localhost"
                    self.initData(alreadyRetried=True)
                else:
                    raise e
        else:
            self.data = dict()

    def reset(self, security=False):
        if self.useMongodb:
            self.data.resetCollection(security=security)
        else:
            self.removeFile()
        self.initData()

    def keys(self):
        return list(self.data.keys())

    def conditionalClean(self):
        if self.cleanEachNAction is not None and self.cleanEachNAction > 0:
            if self.actionCount % self.cleanEachNAction == 0:
                self.clean()

    def getToDeleteOlder(self, toDeleteCount):
        sortedIndex = []
        if self.useMongodb:
            theIterator = self.data.items(projection={"modified": 1, "read": 1})
        else:
            theIterator = self.data.items()
        for key, value in theIterator:
            currentModified = value["modified"]
            currentRead = value["read"]
            toTake = currentModified
            if currentRead > currentModified:
                toTake = currentRead
            sortedIndex.append((key, toTake))
        sortedIndex = sortBy(sortedIndex, desc=False, index=1)
        toDelete = set()
        for i in range(toDeleteCount):
            toDelete.add(sortedIndex[i][0])
        return toDelete

    def dataSizeMo(self):
        """
            Warning getsizeof doesn't give real size of a dict because it can keep a huge size for performance issue, so we have to calculate the data size on each element:
            https://stackoverflow.com/questions/11129546/python-sys-getsizeof-reports-same-size-after-items-removed-from-list-dict
        """
        total = 0
        for key, value in self.data.items():
            total += objectSizeMo(key)
            total += objectSizeMo(value)
        return total

    def clean(self):
        cleanedCount = 0
        if self.cleanNotReadOrModifiedSinceNSeconds is not None and self.cleanNotReadOrModifiedSinceNSeconds > 0:
            toDelete = set()
            for key, current in self.data.items():
                modifiedInterval = time.time() - current["modified"]
                readInterval = time.time() - current["read"]
                if modifiedInterval > self.cleanNotReadOrModifiedSinceNSeconds or \
                readInterval > self.cleanNotReadOrModifiedSinceNSeconds:
                    toDelete.add(key)
            for current in toDelete:
                del self.data[current]
            cleanedCount += len(toDelete)
        if self.cleanMaxValueCountReadModifiedOlder is not None and \
        self.cleanMaxValueCountReadModifiedOlder > 0 and \
        self.size() > self.cleanMaxValueCountReadModifiedOlder:
            toDeleteCount = self.size() - self.cleanMaxValueCountReadModifiedOlder
            toDelete = self.getToDeleteOlder(toDeleteCount)
            cleanedCount += len(toDelete)
            for current in toDelete:
                del self.data[current]
        if not self.useMongodb:
            if self.cleanMaxSizeMoReadModifiedOlder is not None and \
            self.cleanMaxSizeMoReadModifiedOlder > 0:
                while self.dataSizeMo() > self.cleanMaxSizeMoReadModifiedOlder:
                    toDeleteCount = self.size() // 20 # We delete 5%
                    toDelete = self.getToDeleteOlder(toDeleteCount)
                    cleanedCount += len(toDelete)
                    for current in toDelete:
                        del self.data[current]
        # Here you can other "clean condition"
        # ...
        if cleanedCount > 0:
            pass
            log(str(cleanedCount) + " items were cleaned from " + self.filePath, self)

    def size(self):
        return len(self.data)


# DEPRECATED
class SerializableHashMap():
    # class Value(): # Todo date history, object, max number (limit)...

    def __init__(self, filePath, compresslevel=0):
        print("This class is deprecated, use SerializableDict instead")
        self.data = dict()
        self.filePath = filePath
        self.compresslevel = compresslevel
        self.load()

    def serialize(self):
        f = None
        if self.compresslevel > 0:
            f = gzip.GzipFile(self.filePath, 'w', compresslevel=self.compresslevel)
        else:
            f = open(self.filePath, 'w')
        try:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
        finally:
            f.close()

    def add(self, key, value):
        self.data[key] = value

    def getOne(self, *args, **kwargs):
        return self.get(*args, **kwargs)
    def get(self, key):
        if key in self:
            return self.data[key]
        else:
            return None

    def hasKey(self, *args, **kwargs):
        return self.has_key(*args, **kwargs)
    def has_key(self, key):
        return key in self.data

    def load(self):
        if (len(sortedGlob(self.filePath)) > 0):
            print("Loading " + self.filePath + " from the disk")
            f = None
            if self.compresslevel > 0:
                f = gzip.GzipFile(self.filePath, 'r', compresslevel=self.compresslevel)
            else:
                f = open(self.filePath, 'r')
            try:
                self.data = pickle.load(f)
            finally:
                f.close()

    def clean(self):
        if (len(sortedGlob(self.filePath)) > 0):
            os.remove(self.filePath)
        self.data = dict()

    def size(self):
        return len(self.data)


class SentencePair:
    def __init__(self, s1, s2):
        assert(isinstance(s1, str) or isinstance(s1, str))
        assert(isinstance(s2, str) or isinstance(s1, str))
        self.s1 = s1
        self.s2 = s2

    def __hash__(self):
        return (self.s1 + "\t" + self.s2).__hash__()

    def __eq__(self, other):
        return (self.s1 == other.s1) and (self.s2 == other.s2)

    def __str__(self):
        if isinstance(self.s1, str):
            return str(self.s1) + "\t" + str(self.s2)
        elif isinstance(self.s1, str):
            import unicodedata
            return unicodedata.normalize('NFKD', self.s1 + "\t" + self.s2).encode('ascii','ignore')
        else:
            return "Unknown object."


if __name__ == '__main__':
    sd = SerializableDict()
    sd["a"] = 1
    print(sd["a"])
    del sd["a"]
    print(sd["a"])
