import os
import sys
import logging

from ConfigParser import ConfigParser
from client import ImageClient

try:
    import multiprocessing
except:
    multiprocessing = None

DEFAULT_MAX_DIMENSION = 3000
DEFAULT_BIND_PORT = 6776

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
    logging.error("Could not detect number of processors; assuming 1")
    return 1


class Config(object):

    def __init__(self, host='127.0.0.1', 
                 port=DEFAULT_BIND_PORT,
                 max_dimension=DEFAULT_MAX_DIMENSION,
                 master=None, slaves=None, num_procs=None):
        self._host = host
        self._port = port
        self._num_procs = num_procs or cpu_count()
        self._master = master
        self._slaves = slaves or []
        self._max_dimension = max_dimension

    def get_port(self):
        return self._port
    def set_port(self, port):
        self._port = port
    port = property(get_port, set_port)

    def get_host(self):
        return self._host
    def set_host(self, host):
        self._host = host
    host = property(get_host, set_host)

    def get_num_procs(self):
        return self._num_procs
    def set_num_procs(self, np):
        self._num_procs = np
    num_procs = property(get_num_procs, set_num_procs)

    @property
    def get_master(self):
        return self._master

    @property
    def get_slaves(self):
        return self._slaves

    def get_max_dimension(self):
        return self._max_dimension
    def set_max_dimension(self, dimen):
        self._max_dimension = dimen
    max_dimension = property(get_max_dimension, set_max_dimension)


    def add_slave(self, slave):
        self._slaves.append(slave)

    def set_master(self, master):
        self._master = master

    @classmethod
    def from_file(self, filename):
        cp = ConfigParser()
        if os.path.exists(filename):
            cp.read(filename)
        else:
            sys.stderr.write("Config file (%s) not found\n" % filename)
            raise SystemExit

        bind_host = '127.0.0.1'
        bind_port = DEFAULT_BIND_PORT
        max_dimension = DEFAULT_MAX_DIMENSION
        num_procs = cpu_count()
        master = None
        slaves = []

        # TODO: make this a lot less ugly
        for section in cp.sections():
            options = cp.options(section)
            if section.lower().startswith('slave'):
                slave = ImageClient(cp.get(section, 'host'),
                                    port=cp.get(section, 'port')\
                                        if 'port' in options else 80)
                slaves.append(slave)
            elif section == 'properties':
                bind_port = cp.get(section, 'bind_port') \
                    if 'bind_port' in options else DEFAULT_BIND_PORT
                bind_host = cp.get(section, 'bind_host') \
                    if 'bind_host' in options else 'localhost'
                max_dimension = cp.get(section, 'max_dimension') \
                    if 'max_dimension' in options else DEFAULT_MAX_DIMENSION
                
            elif section == 'master':
                master = ImageClient(cp.get(section, 'host'),
                                     port=cp.get(section, 'port')\
                                         if 'port' in options else 80)

        return Config(
            host=bind_host, 
            port=bind_port,
            max_dimension=max_dimension,
            num_procs=num_procs,
            master=master, 
            slaves=slaves)
