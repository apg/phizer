#!/usr/bin/env python
"""
"""
import os
import re
import sys
import traceback
import httplib

from StringIO import StringIO
from PIL import Image


class ImageClient(object):
    """Represents a place in which images can come from.
    """

    def __init__(self, host, port=80):
        self._host = host
        self._port = port

    def _get_connection(self):
        return httplib.HTTPConnection(self._host, port=self._port, timeout=2)

    def _get(self, path, headers=None):
        """Returns `None` if path is not in the connected resource
        Otherwise, returns `(HTTPResponse, data)` 
        """
        conn = None
        try:
            conn = self._get_connection()
            print conn
            if headers:
                conn.request('GET', path, headers=headers)
            else:
                conn.request('GET', path)
            resp = conn.getresponse()
            print resp
            if str(resp.status)[0] == '2':
                return (resp, resp.read())
            return None
        except Exception, e:
            print >>sys.stderr, "failed to get %s: %s" % (path, e)
            traceback.print_exc(file=sys.stderr)
        finally:
            if conn:
                conn.close()

    def open(self, path):
        """Opens a PIL.Image from a resource obtained via _get
        """
        resp_data = self._get(path)
        
        if resp_data:
            # here we go
            try:
                dat = StringIO(resp_data[1])
                return Image.open(dat)
            except Exception, e:
                return None
        return None

    def __repr__(self):
        return '<ImageClient: host=%s, port=%s>' % (self._host, self._port)
