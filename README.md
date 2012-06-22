# phizer - a dynamic image resizer

## Overview

phizer is a dynamic image resizer proxy that can talk to a number of
image servers. phizer does not do caching like you might expect from
a proxy. Instead, it lets your CDN or other caching proxy do that.

## Requirements

phizer is being written to target Python 2.7, though it is not using
anything that would make it incompatible with 2.6. phizer uses 
multiprocessing to start up multiple processes, and handles resizing
using the [Python Imaging Library](http://www.pythonware.com/products/pil/).

Keep in mind that PIL has it's own requirements. On debian, this entails
installing libjpeg62-dev for jpeg support.

## Hacking

To hack on phizer, simply install the items in requirements.txt. You might
like to use virtualenv and pip to manage that for you.

    $ apt-get install libjpeg62-dev # if you want JPEG support!
    $ virtualenv phienv
    $ . ./phienv/bin/activate
    $ python setup.py develop
    
You may need to run this before the last step.
    $ pip -E $VIRTUAL_ENV -r requirements.txt install 
  
Then, to start, create a config file, and run ./phienv/bin/phizer -c <configfile>
(eg, use 8lt config file - it's in 8lt/etc/phizer/phizer.conf)

Happy hacking!
