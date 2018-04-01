from multiprocessing import cpu_count, Process, Pipe, Queue
from multiprocessing import Pool as MPPool
from systemtools.basics import *
from systemtools.duration import *
from systemtools.logger import *
from pathos.multiprocessing import ProcessingPool as PathosPool
from threading import *
from enum import Enum
from multiprocessing.dummy import Pool as DummyPool
import concurrent
import string
import random


MAP_TYPE = Enum("MAP_TYPE", "sequential builtin pathos multiprocessing parmap dummy spark multithreadMap concurrent_map")
sparkAlreadyImported = False
class Pool:
    """
        Best choice : parmap, multiprocessing and spark
        You must compare before use at production. The perf depends on many things
    """
    def __init__ \
    (
        self,
        parallelCount=None,
        verbose=True,
        logger=None,
        mapType=MAP_TYPE.pathos,
        sparkDriverMaxResultSize=2,
        sparkDriverMemory=2,
        sparkExecutorMemory=2,
    ):
        self.logger = logger
        self.verbose = verbose
        self.parallelCount = parallelCount
        self.mapType = mapType

        # Spark:
        self.sparkDriverMaxResultSize = sparkDriverMaxResultSize
        self.sparkDriverMemory = sparkDriverMemory
        self.sparkExecutorMemory = sparkExecutorMemory

        if self.parallelCount is None:
            self.parallelCount = cpu_count()
        if self.mapType == MAP_TYPE.multiprocessing:
            self.pool = MPPool(self.parallelCount)
        elif self.mapType == MAP_TYPE.pathos:
            self.pool = PathosPool(self.parallelCount)
        elif self.mapType == MAP_TYPE.dummy:
            self.pool = DummyPool(self.parallelCount)
        elif self.mapType == MAP_TYPE.spark:
            try:
                global sparkAlreadyImported
                if not sparkAlreadyImported:
                    import findspark
                    findspark.start()
                    import pyspark
                    from pyspark import SparkContext, SparkConf
                    conf = \
                    {
                        "spark.driver.maxResultSize": str(self.sparkDriverMaxResultSize) + "g",
                        "spark.driver.memory": str(self.sparkDriverMemory) + "g",
                        "spark.executor.memory": str(self.sparkExecutorMemory) + "g",
                        "spark.master": "local[" + str(self.parallelCount) + "]"
                    }
                    sparkConf = SparkConf()
                    sparkConf.setAppName('Pool Spark')
                    for key, value in conf.items():
                        sparkConf.set(key, value)
                    self.sc = SparkContext(conf=sparkConf)
                    sparkAlreadyImported = True
            except Exception as e:
                logException(e, self, message="Unable to load Spark!")
                sparkAlreadyImported = False
            self.pool = None
        else:
            self.pool = None

    def isSpark(self):
        return self.mapType == MAP_TYPE.spark and sparkAlreadyImported

    def map(self, funct, data):
        result = None
        if callable(data):
            (funct, data) = (data, funct)
        if self.pool is None:
            if self.isSpark():
                # TODO maybe udf for memory sharing ??? --> test on detecor 404
                # TODO faire une boucle aussi qui boucle sur tous les MAP_TYPE
                data = self.sc.parallelize(data)
                result = data.map(funct).collect()
            elif self.mapType == MAP_TYPE.parmap:
                result = parmap(funct, data, nprocs=self.parallelCount)
            elif self.mapType == MAP_TYPE.multithreadMap:
                result = multithreadMap(funct, data, threadNumber=self.parallelCount)
            elif self.mapType == MAP_TYPE.concurrent_map:
                result = concurrent_map(funct, data)
            elif self.mapType == MAP_TYPE.sequential:
                result = [funct(r) for r in data]
            else:
                result = map(funct, data)
        else:
            result = self.pool.map(funct, data)
        return list(result)

def multithreadMap(funct, data, threadNumber=cpu_count()):
    def execute(dataChunk, currentDataIndex):
        for u, element in enumerate(dataChunk):
            resultIndex = currentDataIndex + u
            result[resultIndex] = funct(element)
    if callable(data):
        (funct, data) = (data, funct)
    result = [None] * len(data)
    data = chunks(data, threadNumber)
    threads = []
    currentDataIndex = 0
    for dataChunk in data:
        currentThread = Thread(target=execute, args=(dataChunk, currentDataIndex))
        threads.append(currentThread)
        currentThread.start()
        currentDataIndex += len(dataChunk)
    for currentThread in threads:
        currentThread.join()
    return result

def enumerate(sequence, start=0):
    n = start
    for elem in sequence:
        yield n, elem
        n += 1

def fun(f, q_in, q_out):
    while True:
        i, x = q_in.get()
        if i is None:
            break
        q_out.put((i, f(x)))


def parmap(f, X, nprocs=cpu_count()):
    q_in = Queue(1)
    q_out = Queue()

    proc = [Process(target=fun, args=(f, q_in, q_out))
            for _ in range(nprocs)]
    for p in proc:
        p.daemon = True
        p.start()

    sent = [q_in.put((i, x)) for i, x in enumerate(X)]
    [q_in.put((None, None)) for _ in range(nprocs)]
    res = [q_out.get() for _ in range(len(sent))]

    [p.join() for p in proc]

    return [x for i, x in sorted(res)]


def concurrent_map(func, data):
    """
    Similar to the bultin function map(). But spawn a thread for each argument
    and apply `func` concurrently.

    Note: unlike map(), we cannot take an iterable argument. `data` should be an
    indexable sequence.

    WARNING : this function doesn't limit the number of threads at the same time
    """

    N = len(data)
    result = [None] * N

    # wrapper to dispose the result in the right slot
    def task_wrapper(i):
        result[i] = func(data[i])

    threads = [Thread(target=task_wrapper, args=(i,)) for i in range(N)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    return result


def lowerAndAdd(text):
    return text.lower() + getRandomStr()

def randomData(input):
    return getRandomStr() + "-------A-------" + getRandomStr()

class Test():
    def __init__(self):
        self.randomLetter = {"data": random.choice(string.ascii_uppercase)}
    def getData(self):
        return self.randomLetter["data"] + str("x")
    def execute1(self, element):
        return getRandomStr() + "-------" + self.getData() + "-------" + getRandomStr()
    def execute2(self, text):
        return text.lower() + getRandomStr() + "--" + self.getData()

def test01():
    for current in MAP_TYPE:
#         if current == MAP_TYPE.spark:
        for (funct1, funct2) in \
        [
#             (randomData, lowerAndAdd),
            (Test().execute1, Test().execute2),
        ]:
            try:
                tt = TicToc()
                tt.tic(str(current))
                tp = Pool(mapType=current)
                data = list([0] * 10) # 1000000
                data = tp.map(data, funct1)
                result = tp.map(data, funct2)
                printLTS(result[-3:-1])
                tt.toc("\n\n\n")
            except Exception as e:
                logException(e)
                print("\n\n\n")








if __name__ == '__main__':
    test01()





"""

--> toc total duration: 1m 10.680000000000007s | message: parmap
--> toc total duration: 16.19s | message: pathos
--> toc total duration: 8.88s | message: multiprocessing
--> toc total duration: 33.01s | message: dummy
--> toc total duration: 32.76s | message: map
--> toc total duration: 35.22s | message: serialized
--> toc total duration: 2m 34.28999999999999s | message: concurrent_map


"""








