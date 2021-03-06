from optparse import OptionParser

import sys
import logging

from tornado.options import options as toptions
from phizer.config import Config, DEFAULT_PROPERTIES

toptions.logging = 'none'


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
parser.add_option('-l', '--log-level', default=None, dest='loglevel',
                  help="log level to use (ERROR, INFO, DEBUG, WARN, CRITICAL)")
parser.add_option('-w', '--log-level-worker', default=None, dest='loglevel_worker',
                  help="log level to use (ERROR, INFO, DEBUG, WARN, CRITICAL)")
parser.add_option('-n', '--num-workers', dest="num_workers", type="int",
                  default=None, help="number of workers to run (default=%d)" % \
                      DEFAULT_PROPERTIES['num_workers'])
parser.add_option('-p', '--port', dest="port", type="int", default=None,
                  help="port to bind to (default=%d)" % \
                      DEFAULT_PROPERTIES['bind_port'])

def main():
    from phizer.server import run_pool

    (options, args) = parser.parse_args()
    conf = Config.from_file(options.config)

    level = logging.INFO
    worker_level = logging.INFO

    fmt = '%(levelname)s pid=%(process)s %(message)s'
    
    if options.host:
        conf.set('bind_host', options.host)
    if options.port:
        conf.set('bind_port', options.port)
    if options.num_workers:
        conf.set('num_workers', options.num_workers)
    if options.dimension:
        conf.set('max_dimension', options.dimension)
    if options.max_age:
        conf.set('max_age', options.max_age)
    if options.disable_cache:
        conf.set('disable_cache', options.disable_cache)

    if options.loglevel:
        conf.set('log_level', options.loglevel)
    if options.loglevel == 'DEBUG':
        conf.set('debug', True)
    if options.loglevel_worker:
        conf.set('log_level_worker', options.loglevel_worker)

    level = logging.getLevelName(conf.log_level)
    worker_level = logging.getLevelName(conf.log_level_worker)
    print level, conf.log_level, worker_level, conf.log_level_worker

    if not isinstance(level, int):
        print >>sys.stderr, "\nInvalid log level parameter\n"
        parser.print_help()
        sys.exit(1)
    if not isinstance(worker_level, int):
        print >>sys.stderr, "\nInvalid log level parameter for worker\n"
        parser.print_help()
        sys.exit(1)

    logging.basicConfig(level=level, format=fmt)
    run_pool(conf, level=level, worker_level=worker_level)

