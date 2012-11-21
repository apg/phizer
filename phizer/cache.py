try:
    from collections import OrderedDict
except ImportError:
    from phizer.ordereddict import OrderedDict

from collections import namedtuple

import time

cached_image = namedtuple('cached_image', 
                          ['body', 'content_type', 'size'])

class LRUCache(object):
    """poor man's LRU
    """

    def __init__(self, size):
        self._size = size
        self._order = OrderedDict()
        self._cache = {}

        self.DEBUG = True
        self.DEBUG_NAME = None

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
                if self.DEBUG:
                    print "PURGE from %s from %s" % (key, self.DEBUG_NAME)
                del self._cache[key]
            except:
                pass
