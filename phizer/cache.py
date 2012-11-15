from threading import RLock

try:
    from collections import OrderedDict
except ImportError:
    from phizer.ordereddict import OrderedDict

import time

# pointless!
AUTHKEY = 'CACHE MONEY'


class LRUCache(object):
    """poor man's LRU
    """
    
    def __init__(self, size):
        self._size = size
        self._order = OrderedDict()
        self._cache = {}

    def get(self, key):
        if key in self._cache:
            self.touch(key)
        return self._cache.get(key)

    def put(self, key, val):
        try:
            del self._order[key]
        except:
            pass

        self._cache[key] = val
        self.touch(key)
        self._purge()

    def delete(self, key):
        try:
            del self._cache[key]
            del self._order[key]
        except:
            pass

    def touch(self, key):
        if key in self._order:
            del self._order[key]
        self._order[key] = time.time()

    def size(self):
        return len(self._cache)

    def _purge(self):
        while len(self._cache) > self._size and len(self._order) > 0:
            key, _ = self._order.popitem(last=False)
            try:
                del self._cache[key]
            except:
                pass


class SafeCache(object):
    """Provides a multiprocessing Manager for image caching
    """

    def __init__(self, cache):
        self.__cache = cache
        self.__lock = RLock()

    def get(self, key):
        with self.__lock:
            return self.__cache.get(key)

    def put(self, key, value):
        with self.__lock:
            return self.__cache.put(key, value)

    def delete(self, key):
        with self.__lock:
            return self.__cache.delete(key)

    def size(self):
        return self.__cache.size()

