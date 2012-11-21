try:
    from collections import OrderedDict
except ImportError:
    from phizer.ordereddict import OrderedDict

import operator
import sys

from collections import namedtuple

cached_image = namedtuple('cached_image', 
                          ['body', 'content_type', 'size'])


class SizedLRUCache(object):

    def __init__(self, max_size=None):
        self._max_size = max_size
        self._current_size = 0
        self._cache = OrderedDict()

    def get(self, key):
        value = self._cache.pop(key)
        self._cache[key] = value
        return value

    def put(self, key, value):
        self._cache.pop(key, None)
        self._update_current_size(value)

        if self._current_size > self._max_size:
            self._purge()

        self._cache[key] = value

    def delete(self, key):
        _ = self._cache.pop(key)
        self._update_current_size(value, operator.sub)

    def touch(self, key):
        """'uses' item at key, thereby making it recently used
        """
        value = self._cache.pop(key)
        self._cache[key] = value

    @property
    def size(self):
        return self._current_size

    def _update_current_size(self, value, f=operator.add):
        self._current_size = f(self._current_size, sys.getsizeof(value))

    def __len__(self):
        """Returns the number of items in the cache"""
        return len(self._cache)

    def _purge(self):
        """Purges least recently used items until less than `max_size`
        """
        if self._max_size is None:
            return

        while self._current_size > self._max_size and len(self) > 0:
            key, value = self._cache.popitem(True)
            self._update_current_size(value, operator.sub)
