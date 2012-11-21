#!/usr/bin/env python
"""
"""
import os
import re
import sys
import traceback
import urllib

import tornado.httpclient as thc
from tornado import gen

from cStringIO import StringIO
from phizer.cache import cached_image

try:
    import Image
except ImportError:
    from PIL import Image


class ImageClient(object):

    def __init__(self, host, port=80, root='/', cache=None):
        self._host = host
        self._port = port
        self._root = root
        self._cache = cache

    @property
    def client(self):
        return thc.AsyncHTTPClient()

    @gen.engine
    def open(self, path, callback=None):
        """Asynchronously opens an image from a remote resource
        """
        cimg = None
        if self._cache:
            try:
                cimg = self._cache.get(path)
            except KeyError:
                pass

        if not cimg:
            url = self.url_for(path)
            response = yield gen.Task(self.client.fetch, url)
            if response.error:
                callback(None)
                return 

            ctype = response.headers.get('Content-Type')
            cimg = cached_image(body=response.body,
                                content_type=ctype,
                                size=len(response.body))

            if self._cache:
                self._cache.put(path, cimg)

        if cimg and callback:
            callback(Image.open(StringIO(cimg.body)))
        elif callback:
            callback(None)
        return

    def url_for(self, path):
        return urllib.basejoin('http://%s:%s%s' % (self._host, 
                                                self._port, 
                                                self._root),
                               path)
        
