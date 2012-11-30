#!/usr/bin/env python
"""
"""
import os
import re
import sys
import urllib
import logging

from collections import defaultdict
from cStringIO import StringIO

import tornado.httpclient as thc
from tornado import gen

from phizer.cache import cached_image

try:
    import Image
except ImportError:
    from PIL import Image


class ImageClient(object):

    def __init__(self, host, port=80, root='/', cache=None, max_clients=100):
        self._host = host
        self._port = port
        self._root = root
        self._cache = cache
        self._max_clients = max_clients
        self._inflight = defaultdict(list)

    @property
    def client(self):
        return thc.AsyncHTTPClient(max_clients=self._max_clients)

    def on_fetch(self, response):
        im = None
        if response.error:
            logging.error('%s got a %s %s', 
                          response.request.url, 
                          response.code,
                          response.error)
        else:
            ctype = response.headers.get('Content-Type')
            cimg = cached_image(body=response.body,
                                content_type=ctype,
                                size=len(response.body))

            if self._cache:
                self._cache.put(path, cimg)
            
            im = Image.open(StringIO(cimg.body))

        waiters = self._inflight.pop(response.request.url)
        logging.debug('popping %s waiters for %s', len(waiters),
                      response.request.url)
        for c in waiters:
            c(im)

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
            already_in_flight = url in self._inflight[url]
            self._inflight[url].append(callback)
            if not already_in_flight:
                self.client.fetch(url, callback=self.on_fetch)
        else:
            callback(Image.open(StringIO(cimg.body)))

    def url_for(self, path):
        return urllib.basejoin('http://%s:%s%s' % (self._host, 
                                                   self._port, 
                                                   self._root),
                               path)
