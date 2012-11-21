import os
import sys
import re

from collections import namedtuple
from ConfigParser import SafeConfigParser as ConfigParser
from client import ImageClient

import logger

try:
    import multiprocessing
except:
    multiprocessing = None

DEFAULT_MAX_DIMENSION = 3000
DEFAULT_BIND_PORT = 6776

sizespec = namedtuple('sizespec', 'w h t attrs')

# lifted from tornado web.
def cpu_count():
    """Returns the number of processors on this machine."""
    if multiprocessing is not None:
        try:
            return multiprocessing.cpu_count()
        except NotImplementedError:
            pass
    try:
        return os.sysconf("SC_NPROCESSORS_CONF")
    except ValueError:
        pass
    logger.error("Could not detect number of processors; assuming 1")
    return 1

def parse_size(s):
    attrs = {}

    (_, w, h, t, a, _) = re.split('(\d+)(?:x|,)?\s*(\d+)?\s+'
                                  '(portrait|landscape|square|max)?'
                                  '\s*((?:\w+=\w+)(?:,\s*(?:\w+=\w+))*)?',
                                  s.strip())
    if a:
        attrs = dict(kv.split('=') for kv in 
                     (p.strip() for p in a.split(',')))

    w = int(w)
    if h:
        h = int(h)
    else:
        h = -1

    if t:
        if t == 'portrait' and w > h:
            raise ValueError(
                "For portrait sizing, width can't be greater than height")
        elif t == 'landscape' and w < h:
            raise ValueError(
                "For landscape sizing, height can't be greater than width")
        elif t == 'square' and w != h:
            w = max(bits1, bits2)
            h = w
        elif t == 'max' and h < 0:
            h = w

    return sizespec(w, h, t, attrs)

DEFAULT_NUM_WORKERS = cpu_count()
if DEFAULT_NUM_WORKERS > 1:
    DEFAULT_NUM_WORKERS -= 1 # 

DEFAULT_PROPERTIES = {
    'bind_host': 'localhost',
    'bind_port': 6776,
    'cache_authkey': 'CACHE',
    'cache_port': 6777,
    'cache_size': 10000,
    'canvas_color': '#ffffff', # TODO: allow this to be set!
    'debug': False,
    'disable_cache': False,
    'image_quality': 95, # image save quality (affects JPEG only)
    'max_age': 0,        # cache max age
    'max_dimension': 3000,
    'num_workers': DEFAULT_NUM_WORKERS,
    'syslog_facility': None,
    'syslog_priority': 'LOG_ERR',
}

PROPERTY_TYPES = {
    'bind_host': str,
    'bind_port': int,
    'cache_authkey': str,
    'cache_port': int,
    'cache_size': int,
    'canvas_color': str,
    'debug': bool,
    'disable_cache': bool,
    'image_quality': int,
    'max_age': int,
    'max_dimension': int,
    'num_workers': int,
    'syslog_facility': str,
    'syslog_priority': str,
}


class Config(object):

    def __init__(self, properties=None, master=None, slaves=None, sizes=None):
        self._properties = properties or DEFAULT_PROPERTIES.copy()
        self._master = master
        self._slaves = slaves or []
        self._sizes = sizes or {}

    def __getattribute__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError, e:
            if attr in self._properties:
                return self._properties[attr]
            raise e

    def set(self, attr, val):
        if attr in self._properties:
            self._properties[attr] = val
        else:
            logger.error("CONFIG: attempting to set property that "
                          "doesn't exist")

    def get_master(self):
        return self._master
    def set_master(self, master):
        self._master = master
    master = property(get_master, set_master)


    @property
    def sizes(self):
        return self._sizes

    def set_size(self, s, val):
        self._sizes[s] = val

    @property
    def slaves(self):
        return self._slaves

    def add_slave(self, slave):
        self._slaves.append(slave)

    @classmethod
    def from_file(self, filename):
        cp = ConfigParser()
        if os.path.exists(filename):
            cp.read(filename)
        else:
            sys.stderr.write("Config file (%s) not found\n" % filename)
            raise SystemExit

        master = None
        slaves = []

        properties = DEFAULT_PROPERTIES.copy()
        sizes = {}

        # TODO: Clients now can have a cache, use it!
        # TODO: make this a lot less ugly
        for section in cp.sections():
            options = cp.options(section)
            if section.lower().startswith('slave'):
                slave = ImageClient(cp.get(section, 'host'),
                                    port=cp.get(section, 'port')\
                                        if 'port' in options else 80,
                                    root=cp.get(section, 'root')\
                                         if 'root' in options else '/')
                slaves.append(slave)
            elif section == 'properties':
                # build properties and set to logical types

                # might be good to do validation here, but, meh.
                for o in options:
                    t = PROPERTY_TYPES.get(o)
                    if t:
                        properties[o] = t(cp.get(section, o))
                    else:
                        logger.warn("CONFIG: don't know about option %s "
                                     "in properties section" % o)

            elif section == 'master':
                master = ImageClient(cp.get(section, 'host'),
                                     port=int(cp.get(section, 'port'))\
                                         if 'port' in options else 80,
                                     root=cp.get(section, 'root')\
                                         if 'root' in options else '/')
            elif section == 'sizes':
                for o in options:
                    try:
                        sizes[o] = parse_size(cp.get(section, o))
                    except:
                        logger.warn("CONFIG: don't know how to parse "
                                     "dimensions for size '%s'" % o)

        return Config(
            properties=properties,
            master=master, 
            slaves=slaves,
            sizes=sizes)
