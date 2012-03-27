#!/usr/bin/env python
"""
"""
import os
import re
import sys
import traceback
import httplib
import logging
import heapq

from StringIO import StringIO
from PIL import Image

from phizer.cache import LRUCache

class ImageClient(object):
    """Represents a place in which images can come from.
    """

    def __init__(self, host, port=80, root='/', cache=None):
        self._host = host
        self._port = port
        self._root = root
        self._cache = cache

    def _get_connection(self):
        return httplib.HTTPConnection(self._host, port=self._port, timeout=2)

    def _get(self, path, headers=None):
        """Returns `None` if path is not in the connected resource
        Otherwise, returns `(HTTPResponse, data)` 
        """
        conn = None
        try:
            conn = self._get_connection()
            if headers:
                conn.request('GET', path, headers=headers)
            else:
                conn.request('GET', path)
            resp = conn.getresponse()
            if str(resp.status)[0] == '2':
                return (resp, resp.read())
            return None
        except Exception, e:
            logging.exception("failed to get %s")
        finally:
            if conn:
                conn.close()

    def path(self, path):
        if self._root.endswith('/') and path.startswith('/'):
            return self._root[:-1] + path

        return self._root + path
    
    def open(self, path):
        """Opens a PIL.Image from a resource obtained via _get
        """
        path = self.path(path)
        cached = self._cache.get(path)
        if cached:
            return Image.open(cached)

        resp_data = self._get(path)
        
        if resp_data:
            # here we go
            try:
                dat = StringIO(resp_data[1])
                cached.put(path, dat)
                return Image.open(dat)
            except Exception, e:
                logging.exception("failed to open response data")
                return None
        return None

    def set_cache(self, cache):
        self._cache = cache

    def get_cache(self):
        return self._cache

    cache = property(get_cache, set_cache)

    def __repr__(self):
        return '<ImageClient: host=%s, port=%s, root=%s>' % \
            (self._host, self._port, self._root)
