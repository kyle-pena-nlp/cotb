import math, time
import wrapt
from collections import deque

INSTRUMENTED_COLLECTIONS = []
INSTANCE_COUNT = [0]
ops   = []
space = []

def take_snapshot():
    ops.append(_get_total_ops())
    space.append(INSTANCE_COUNT[0])
    return {
        "ops": ops,
        "space": space
    }

def _get_total_ops():
    return sum(instance.get_ops() for instance in INSTRUMENTED_COLLECTIONS)

def _get_total_space():
    return sum(instance.get_space() for instance in INSTRUMENTED_COLLECTIONS)

def reset_instrumentation():
    ops.clear()
    space.clear()

# The following proxies record the time and space complexity of an object's usage for later analysis
# Each proxy must have a get_space and get_ops method which return numbers
# Costs are the average case for simplicity
# https://wiki.python.org/moin/TimeComplexity

class InstrumentedSet(wrapt.ObjectProxy):

    def __init__(self, wrapped):
        assert type(wrapped) == set
        super(InstrumentedSet, self).__init__(wrapped)
        self._self_ops = 0.0
        INSTRUMENTED_COLLECTIONS.append(self)

    def add(self, item):
        self._self_ops += 1.0
        self.__wrapped__.add(item)

    def __contains__(self, item):
        self._self_ops += 1.0
        return self.__wrapped__.__contains__(item)

    def get_space(self):
        return len(self.__wrapped__)

    def get_ops(self):
        return self._self_ops



class InstrumentedList(wrapt.ObjectProxy):

    def __init__(self, wrapped):
        assert type(wrapped) == list
        super(InstrumentedList, self).__init__(wrapped)
        self._self_ops = 0.0
        INSTRUMENTED_COLLECTIONS.append(self)

    def append(self, item):
        self._self_ops += 1.0
        self.__wrapped__.append(item)

    def __contains__(self, item):
        try:
            index = self.__wrapped__.index(item)
            self._self_ops += index
            return True
        except ValueError:
            self._self_ops += len(self.__wrapped__)
            return False

    def insert(self, index, item):

        if index is None:
            normalized_index = 0
        elif index < 0:
            normalized_index = len(self.__wrapped__) + index
        else:
            normalized_index = index

        # The cost of "moving up" everything after this position in the list -- notably, this is O(1) at the end of the list
        self._self_ops += len(self.__wrapped__) - normalized_index - 1    

        self.__wrapped__.insert(index, item)    

    def pop(self, index = None):

        if index is None:
            normalized_index = 0
        elif index < 0:
            normalized_index = len(self.__wrapped__) + index
        else:
            normalized_index = index

        # The cost of "moving up" everything after this position in the list -- notably, this is 0(1) at the end of the list
        self._self_ops += len(self.__wrapped__) - normalized_index

        if index is None:
            return self.__wrapped__.pop()
        else:
            return self.__wrapped__.pop(index)

    def sort(self, key = None, reverse = None):
        self._self_ops += len(self.__wrapped__) * math.log(len(self.__wrapped__), 2.0)
        self.__wrapped__.sort(key = key, reverse = reverse)

    def __len__(self):
        self._self_ops += 1
        return len(self.__wrapped__)

    def get_space(self):
        return len(self.__wrapped__)

    def get_ops(self):
        return self._self_ops

class InstrumentedDeque(wrapt.ObjectProxy):

    def __init__(self, wrapped):
        assert type(wrapped) == deque
        super(InstrumentedDeque, self).__init__(wrapped)
        self._self_ops = 0.0
        INSTRUMENTED_COLLECTIONS.append(self)

    def append(self, item):
        self._self_ops += 1.0
        self.__wrapped__.append(item)

    def appendleft(self, item):
        self._self_ops += 1.0
        self.__wrapped__.appendleft(item)

    def pop(self):
        self._self_ops += 1.0
        return self.__wrapped__.pop()

    def popleft(self):
        self._self_ops += 1.0
        return self.__wrapped__.popleft()

    def __contains__(self, item):
        try:
            index = self.__wrapped__.index(item)
            self._self_ops += index
            return True
        except ValueError:
            self._self_ops += len(self.__wrapped__)
            return False

    def insert(self, index, item):
        raise Exception("Uninstrumented") 

    def copy(self):
        raise Exception("Uninstrumented")

    def count(self, item):
        raise Exception("Uninstrumented")        

    def extend(self, items):
        raise Exception("Uninstrumented")        

    def extendleft(self, items):
        raise Exception("Uninstrumented")        

    def remove(self, item):
        raise Exception("Uninstrumented")

    def reverse(self):
        raise Exception("Uninstrumented")

    def rotate(self, n):
        raise Exception("Uninstrumented")

    def __len__(self):
        self._self_ops += 1
        return len(self.__wrapped__)

    def get_space(self):
        return len(self.__wrapped__)

    def get_ops(self):
        return self._self_ops