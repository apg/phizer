from optparse import OptionParser

from phizer.config import Config, DEFAULT_PROPERTIES
from phizer.server import run_pool

import logging
import sys

parser = OptionParser()
parser.add_option('-a', '--max-age', default=None, dest='max_age', type='int',
                  help="max age to cache for - 0 (default) no caching")
parser.add_option('-c', '--config', default='phizer.conf', dest='config',
                  help="config file to load")
parser.add_option('-d', '--max-dimension', default=None, dest='dimension',
                  type="int",
                  help="max dimensional size for images (default=%d)" % \
                      DEFAULT_PROPERTIES['max_dimension'])
parser.add_option('-D', '--disable-cache', action="store_true", dest='disable_cache',
                  help="disable cache")
parser.add_option("-H", "--host", dest="host", default=None,
                  help="host interface to bind to (default=%s)" % \
                      DEFAULT_PROPERTIES['bind_host'])
parser.add_option('-l', '--log-level', default='WARN', dest='loglevel',
                  help="log level to use (ERROR, INFO, DEBUG, WARN, CRITICAL)")
parser.add_option('-n', '--num-procs', dest="num_procs", type="int",
                  default=None, help="number of processes to run (default=%d)" % \
                      DEFAULT_PROPERTIES['num_procs'])
parser.add_option('-p', '--port', dest="port", type="int", default=None,
                  help="port to bind to (default=%d)" % \
                      DEFAULT_PROPERTIES['bind_port'])

def main():
    (options, args) = parser.parse_args()
    conf = Config.from_file(options.config)
    fmt = '%(asctime)s %(levelname)s %(processName)s[%(process)s] %(message)s'
    
    if options.host:
        conf.set('bind_host', options.host)
    if options.port:
        conf.set('bind_port', options.port)
    if options.num_procs:
        conf.set('num_procs', options.num_procs)
    if options.dimension:
        conf.set('max_dimension', options.dimension)
    if options.max_age:
        conf.set('max_age', options.max_age)
    if options.disable_cache:
        conf.set('disable_cache', options.disable_cache)
    if options.loglevel:
        level = logging.getLevelName(options.loglevel)
        if not isinstance(level, int):
            print >>sys.stderr, "\nInvalid log level parameter\n"
            parser.print_help()
            sys.exit(1)

    logging.basicConfig(level=level,
                        format=fmt)

    run_pool(conf)

