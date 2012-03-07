#!/usr/bin/env python
"""
"""
import os
import re
import sys
import traceback
import httplib
import logging

from StringIO import StringIO
from PIL import Image


class ImageClient(object):
    """Represents a place in which images can come from.
    """

    def __init__(self, host, port=80, root='/'):
        self._host = host
        self._port = port
        self._root = root

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
        resp_data = self._get(path)
        
        if resp_data:
            # here we go
            try:
                dat = StringIO(resp_data[1])
                return Image.open(dat)
            except Exception, e:
                logging.exception("failed to open response data")
                return None
        return None

    def __repr__(self):
        return '<ImageClient: host=%s, port=%s, root=%s>' % \
            (self._host, self._port, self._root)
