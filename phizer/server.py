#!/usr/bin/env python
"""
Resizer - Dynamically resize images stored on remote servers.

URLs are of the form:

 Typical resize:
   /(width)x(height)/path.ext

 With cropping points:
   /(width)x(height)/(top-corner-x)x(top-corner-y)/(bottom-right-x)x(bottom-right-y)/path.ext

"""
import os
import re
import sys
import httplib
import hashlib
import random
import time
import logging

from multiprocessing import Process, current_process
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from PIL import Image

from phizer.client import ImageClient
from phizer.proc import resize, crop
from phizer.version import __name__ as program_name
from phizer.version import __version__ as program_version

URL_RE = re.compile('/(?P<size>[a-zA-Z0-9]+)' # size spec
                    '('
                    '/(?P<topx>\d+)x(?P<topy>\d+)' # top left corner
                    '/(?P<botx>\d+)x(?P<boty>\d+)' # bottom right corner
                    ')?/(?P<path>[^/]+\.[a-z]{3})')  # path


class ImageServer(HTTPServer):
    
    def __init__(self, config):
        HTTPServer.__init__(self, (config.bind_host, 
                                   int(config.bind_port)), 
                            ImageHandler)
        self._config = config

    @property
    def config(self):
        return self._config


class ImageHandler(BaseHTTPRequestHandler):
    # we override log_message() to show which process is handling the request

    def log_message(self, format, *args):
        logging.info(format % args)

    def do_GET(self):
        """Interprets self.path and grabs the appropriate image
        """
        # parse URL. If URL leads to valid request, serve it
        mat = URL_RE.match(self.path)
        if not mat:
            return self.error(404, "Not Found")

        gd = mat.groupdict()
        props = dict((k, int(gd[k])) \
                         for k in ('topx', 'topy', 'botx', 'boty') if gd[k])
        dimens = self.get_size(gd['size'])
        if not dimens:
            return self.error(404, 'Not Found')
        else:
            props['width'] = dimens[0]
            props['height'] = dimens[1]

        image = find_image(self.server.config, '/' + mat.groupdict()['path'])
        if image:
            fmt = image.format
            if 'topx' in props:
                image = crop(self.server.config, image, **props)
                logging.debug('size after crop: %s' % image.size)
            image = resize(self.server.config, image, **props)
            return self.respond(image, fmt)
        return self.error(404, 'Not Found')
    
    def error(self, code, msg=None):
        self.send_response(code, msg)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('<html><body><h1>Not found</h1></body></html>')

    def respond(self, image, format='JPEG'):
        try:
            m = self.mime(format)
        except Exception, e:
            return self.error(500, "Internal error")

        self.send_response(200)
        self.send_header("Content-Type", m)

        if self.server.config.max_age:
            max_age = self.server.config.max_age
            self.send_header("Cache-Control", "max-age=%d" % \
                                 max_age)
            dt = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                               time.gmtime() + max_age)
            self.send_header("Expires", dt)
        self.end_headers()

        image.save(self.wfile, format)

    def get_size(self, st):
        """Looks up size type in config. If found, returns cooresponding
        dimensions, otherwise None
        """
        return self.server.config.sizes.get(st)

    def mime(self, t):
        return {'GIF': 'image/gif',
                'PNG': 'image/png',
                'JPEG': 'image/jpeg'}[t]

    def version_string(self):
        return '%s/%s' % (program_name, program_version)


def serve_forever(server):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def run_pool(config):
    server = ImageServer(config)
    logging.info("starting %d procs" % config.num_procs)

    # create child processes to act as workers
    for i in range(config.num_procs - 1):
        Process(target=serve_forever, args=(server,)).start()

    # TODO: should this become a watch dog?
    serve_forever(server)

def find_image(config, path):
    """Locate an image from the master, or the slaves if
    not found on the master

    TODO: it'd be nice to hit the slaves in parallel, since
    it's likely that only one has the image...
    """
    img = config.master.open(path)
    if img:
        return img

    random.shuffle(config.slaves)
    for slave in config.slaves:
        img = slave.open(path)
        if img:
            return img
    return None

