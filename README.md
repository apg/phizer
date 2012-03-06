# phizer - a dynamic image resizer

## Overview

phizer is a dynamic image resizer proxy that can talk to a number of
image servers. phizer does not do caching like you might expect from
a proxy. Instead, it let's your CDN or other caching proxy do that.

## Requirements

phizer is being written to target Python 2.7, though it is not using
anything that would make it incompatible with 2.6. phizer uses 
multiprocessing to start up multiple processes, and handles resizing
using the [Python Imaging Library](http://www.pythonware.com/products/pil/).

