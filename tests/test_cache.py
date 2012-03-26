from phizer.cache import LRUCache

import unittest


class TestCache(unittest.TestCase):

    def setUp(self):
        self._keys = ['andrew', 'maxp', 'max', 'sean', 
                      'matt', 'chris', 'caroline', 'mike']
                      
    def test_insert(self):
        cache = LRUCache(4)
        for n in self._keys:
            cache.put(n, True)
            self.assertTrue(cache.get(n), "cached value not inserted")

    def test_delete(self):
        cache = LRUCache(8)
        for n in self._keys:
            cache.put(n, True)

        for n in self._keys:
            cache.delete(n)

        for n in self._keys:
            self.assertIsNone(cache.get(n), "key %s should be gone")

        self.assertEquals(cache.size(), 0)

    def test_update(self):
        cache = LRUCache(7)
        for n in self._keys:
            cache.put(n, True)

        for n in self._keys:
            cache.put(n, False)

        for n in self._keys:
            self.assertIsNone(cache.get(self._keys[0]), 
                              "key %s should be gone %s" % (self._keys[0], str(cache._cache)))

    def test_purge(self):
        cache = LRUCache(4)
        for n in self._keys:
            cache.put(n, True)

        for i in range(0, 4):
            self.assertIsNone(cache.get(self._keys[i]), 
                              "key %s should have been purged %s" % \
                                  (self._keys[i], repr(cache._cache)))

    
