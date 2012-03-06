from optparse import OptionParser

from phizer.config import Config
from phizer.server import run_pool

import logging

parser = OptionParser()
parser.add_option('-c', '--config', default='phizer.conf', dest='config',
                  help="config file to load")
parser.add_option('-d', '--max-dimension', default=None, dest='dimension',
                  type="int",
                  help="max dimensional size for images")
parser.add_option("-H", "--host",
                  dest="host", default=None,
                  help="host interface to bind to, defaults '127.0.0.1'")
parser.add_option('-n', '--num-procs', dest="num_procs", type="int",
                  default=None, help="number of processes to run")
parser.add_option('-p', '--port', dest="port", type="int",
                  default=None,
                  help="port to bind to")

def main():
    (options, args) = parser.parse_args()
    conf = Config.from_file(options.config)
    
    if options.host:
        conf.host = options.host
    if options.port:
        conf.port = options.port
    if options.num_procs:
        conf.num_procs = options.num_procs
    if options.dimension:
        conf.max_dimension = options.dimension

    run_pool(conf)

