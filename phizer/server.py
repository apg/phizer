#!/usr/bin/env python
"""
Resizer - Dynamically resize images stored on remote servers.

URLs are of the form:

 Typical resize:
   /(width)x(height)/path.ext

 With cropping points:
   /(width)x(height)/(top-corner-x)x(top-corner-y)/(bottom-right-x)x(bottom-right-y)/path.ext

"""
import binascii
import hashlib
import httplib
import logging
import os
import random
import re
import sys
import time
import urllib

from datetime import datetime

import tornado.ioloop
import tornado.httpclient as thc
import tornado.web as tw
import tornado.process

from tornado import gen

from phizer.client import ImageClient
from phizer.proc import resize, crop
from phizer.cache import SizedLRUCache, cached_image
from phizer.version import __name__ as program_name
from phizer.version import __version__ as program_version

try:
    import pycurl
    AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')
except:
    pass

VERSION_STRING = '%s/%s' % (program_name, program_version)
URL_RE = re.compile('/(?P<size>[a-zA-Z0-9]+)'        # size spec
                    '('
                    '/(?P<topx>\d+)x(?P<topy>\d+)'   # top left corner
                    '/(?P<botx>\d+)x(?P<boty>\d+)'   # bottom right corner
                    ')?'                             # ? = maybe top/bot params
                    '/(?P<path>[^/]+\.[a-z]{3,4})')  # path - extension length is 3-4

MIMES = {
    'JPEG': 'image/jpeg',
    'JPG': 'image/jpeg',
    'GIF': 'image/gif',
    'PNG': 'image/png',
}


def crc32(x):
    return binascii.crc32(x) & 0xffffffff


class BaseRequestHandler(tw.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(BaseRequestHandler, self).\
            __init__(application, request, **kwargs)

    def set_default_headers(self):
        self.set_header('Server', VERSION_STRING)

    def send_404(self):
        self.set_status(404)
        self.write("Not Found")
        self.finish()


class ImageHandler(BaseRequestHandler):
    """Proxies requests to the a FetchResizeHandler (on another server)
    and caches the result.

    For now, we're being dumb and caching the end result, which isn't
    minimizing reads from the external "disk." We'd ideally have a cache
    that caches the full size images as well.

    Note: might be doable with by hashing the filename and choosing the
    image handler that way...
    """

    CACHE = None
    CONFIG = None
    WORKERS = []

    @classmethod
    def set_cache(cls, cache):
        cls.CACHE = cache

    @classmethod
    def set_config(cls, config):
        cls.CONFIG = config

    @classmethod
    def set_workers(cls, workers):
        cls.WORKERS = workers

    @tw.asynchronous
    @gen.engine
    def get(self, path):
        s = time.time()
        try:
            cached = self.CACHE.get(path)
            self.deliver(cached)
            self.flush()
            return
        except KeyError:
            pass

        url = self.get_worker_url(path)
        client = thc.AsyncHTTPClient()
        response = yield gen.Task(client.fetch, url)
        if response.error:
            self.set_status(response.code)
            self.write(str(response.error))
            self.finish()
            return
        else:
            # cache the response
            image = cached_image(body=response.body,
                                 content_type=response.headers.get('Content-Type'),
                                 size=len(response.body))
            self.CACHE.put(path, image)
            self.deliver(image)
            self.finish()
            return 

    def deliver(self, image):
        self.set_status(200)
        self.set_header('Content-Length', image.size)
        self.set_header('Content-Type', image.content_type)

        if self.CONFIG.max_age:
            ma = self.CONFIG.max_age
            self.set_header("Cache-Control", "max-age=%d" % ma)
            dt = datetime.strftime(self.get_expiration(ma),
                                   "%a, %d %b %Y %H:%M:%S GMT")
            self.set_header("Expires", dt)
        self.write(image.body)

    def get_worker_url(self, path):
        """Get's an appropriate worker where the file is likely cached
        """
        # just get the filename of the path...
        name = path.split('/').pop()
        worker = crc32(name) % self.CONFIG.num_workers
        return urllib.basejoin(self.WORKERS[worker], path)

    def get_expiration(self, ma):
        now = time.time()
        nowage = now + ma
        return datetime.fromtimestamp(nowage)


class FetchResizeHandler(BaseRequestHandler):
    """Fetches and resizes based on PATH_INFO and config
    """
    CACHE = None
    CONFIG = None

    def __init__(self, application, request, **kwargs):
        super(FetchResizeHandler, self).\
            __init__(application, request, **kwargs)
        self._resize_time = 0.0
        self._fetch_time = 0.0

    @classmethod
    def set_cache(cls, cache):
        cls.CACHE = cache

    @classmethod
    def set_config(cls, config):
        cls.CONFIG = config

    @tw.asynchronous
    @gen.engine
    def get(self, path):
        mat = URL_RE.match(path)
        if not mat:
            self.send_404()
            return 

        gd = mat.groupdict()
        props = dict((k, int(gd[k])) \
                         for k in ('topx', 'topy', 'botx', 'boty') if gd[k])
        dimens = self.CONFIG.sizes.get(gd['size'])
        if not dimens:
            self.send_404()
            return 
        else:
            props['width'] = dimens[0]
            props['height'] = dimens[1]
            props['algorithm'] = dimens[2]
            
        fetch_start = time.time()
        image = yield gen.Task(self.find_image, gd['path'])
        self._fetch_time = time.time() - fetch_start
        if image:
            fmt = image.format
            resize_start = time.time()
            if 'topx' in props:
                image = crop(self.CONFIG, image, **props)
            image = resize(self.CONFIG, image, **props)
            self._resize_time = time.time() - resize_start
            self.send_image(image, fmt)
        else:
            self.send_404()
            return

        return

    def send_image(self, image, format):
        mime = MIMES[format]
        self.set_status(200)
        self.set_header('Content-Type', mime)
        image.save(self, format, quality=self.CONFIG.image_quality)
        self.finish()

    # overridden to add more information in the log
    def _request_summary(self):
        return self.request.method + " " + self.request.uri + \
            " (" + self.request.remote_ip + ")" + \
            " (fetch in %.2fms)" % (self._fetch_time * 1000.0) + \
            " (resize in %.2fms)" % (self._resize_time * 1000.0) 

    @gen.engine
    def find_image(self, path, callback=None):
        """Locate an image from the master, or the slaves if
        not found on the master

        TODO: it'd be nice to hit the slaves in parallel, since
        it's likely that only one has the image...
        """
        if self.CACHE:
            try:
                img = self.CACHE.get(path)
                if callback:
                    callback(img)
                return
            except KeyError:
                pass

        img = yield gen.Task(self.CONFIG.master.open, path)
        if img:
            if self.CACHE:
                self.CACHE.put(path, img)
            
            if callback:
                callback(img)
            return

        # DO THIS IN PARALLEL INSTEAD
        random.shuffle(self.CONFIG.slaves)
        for slave in self.CONFIG.slaves:
            img = yield gen.Task(slave.open, path)
            if img:
                if callback:
                    callback(img)
                return 

        if callback:
            callback(None)
        return

def run_pool(config, level=logging.INFO, worker_level=logging.INFO):
             
    # Fork processes
    task_id = tornado.process.fork_processes(config.num_workers + 1, max_restarts=100)
    if task_id == 0:
        cls = ImageHandler
        cache = SizedLRUCache(config.resized_cache_size)
        port = config.bind_port

        cls.set_workers(['http://localhost:%d/' % (port+i+1,) \
                                 for i in range(config.num_workers)])
        logging.getLogger().setLevel(level)
    else:
        cls = FetchResizeHandler
        cache = SizedLRUCache(config.client_cache_size)
        port = config.bind_port + task_id
        logging.getLogger().setLevel(worker_level)

    cls.set_config(config)
    cls.set_cache(cache)

    logging.info("Starting %s, task-%d, listening on %d..." % \
                    (cls.__name__, task_id, port))
        
    application = tw.Application([
                (r"(.*)", cls),
                ])
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
