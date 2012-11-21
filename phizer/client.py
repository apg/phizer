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
try:
    import Image
except ImportError:
    from PIL import Image

import logger


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
        image_data = None
        if self._cache:
            image_data = self._cache.get(path)

        if not image_data:
            url = self.url_for(path)
            response = yield gen.Task(self.client.fetch, url)
            if response.error:
                callback(None)
                return 

            image_data = response.body
            if self._cache:
                self._cache.put(path, image_data)

        if image_data and callback:
            callback(Image.open(StringIO(image_data)))
        elif callback:
            callback(None)
        return

    def url_for(self, path):
        return urllib.basejoin('http://%s:%s%s' % (self._host, 
                                                self._port, 
                                                self._root),
                               path)
        
