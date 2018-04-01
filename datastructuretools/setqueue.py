# coding: utf-8

from queue import *
from orderedset import OrderedSet
from threading import Lock


class OrderedSetQueue(Queue):
    """
        https://stackoverflow.com/questions/16506429/check-if-element-is-already-in-a-queue
    """
    def _init(self, maxsize):
        self.cacheLock = Lock()
        self.queue = OrderedSet()
    def _put(self, item):
        with self.cacheLock:
            self.queue.add(item)
    def _get(self):
        with self.cacheLock:
            return self.queue.pop(last=False)
    def __contains__(self, item):
        with self.cacheLock:
            with self.mutex:
                return item in self.queue
    def _qsize(self):
        with self.cacheLock:
            return len(self.queue)
    def size(self):
        return self.qsize()
    def toList(self):
        return queueToList(self, maxsize=self.maxsize)

def queueMean(q):
    q = queueToList(q)
    return sum(q) / len(q)

def cloneQueue(queue, maxsize=0):
    """
        You have to cacheLock all your threads to use this function
    """
    elements = []
    while queue.size() > 0:
        elements.append(queue.get())
    newQueue = OrderedSetQueue(maxsize=maxsize)
    for element in elements:
        newQueue.put(element)
        queue.put(element)
    return newQueue

def queueToList(q, maxsize=0):
    """
        You have to cacheLock all your threads to use this function
    """
    q = cloneQueue(q, maxsize=maxsize)
    elements = []
    while q.size() > 0:
        elements.append(q.get())
    return elements

def listToQueue(l, maxsize=0):
    """
        You have to cacheLock all your threads to use this function
    """
    queue = OrderedSetQueue(maxsize=maxsize)
    for current in l:
        queue.put(current)
    return queue

class NumberQueue:
    def __init__(self, size, defaultValue=None):
        self.size = size
        self.defaultValue = defaultValue
        self.queue = [self.defaultValue] * self.size
        self.index = 0

    def add(self, *agrs, **kwargs):
        self.put(*agrs, **kwargs)

    def put(self, element):
        self.queue[self.index] = element
        self.index += 1
        if self.index == self.size:
            self.index = 0

    def mean(self):
        theSum = 0
        theSize = 0
        for current in self.queue:
            if current is not None:
                theSize += 1
                theSum += current
        return theSum / theSize




if __name__ == '__main__':
    q = NumberQueue(3)
    q.put(1)
    q.put(1)
    q.put(1)
    q.put(1)
    q.put(1)
    q.put(10)
    q.put(10)
    q.put(10)
    print(q.mean())

#     print(q.toList())
#     print(q.maxsize)
#     print(q.get())
#     print(q.get())
#     q.put(2)
#     q.put(3)
#     q.put(3)
#     for current in iter(q):
#         print(current)



