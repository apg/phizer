# phizer - a dynamic PHoto resIZER proxy

## Overview

phizer is a dynamic image resizing proxy that can talk to a number of
image servers. phizer can do caching of the remote fetched images, as
well as the processed images. Put a CDN in front of this, and you've
got yourself a pretty nice prescription for resizing.

## Requirements

phizer targets Python 2.7, though Python 2.6 should work fine as well.
The [tornado web framework](http://www.tornadoweb.org) is being used
for handling I/O, and forking processes for the worker model. It is 
recommended that you install PyCurl, so that tornado can use a more
advanced HTTP client.

Images are being resized/cropped using the 
[Python Imaging Library](http://www.pythonware.com/products/pil/). Keep
in mind that PIL has it's own requirements. On debian, this entails
installing libjpeg62-dev for jpeg support.

## More details

### Architecture

phizer's architecture is a fairly straightforward worker model. Resizing
requests are received by the master process, which has two 
responsibilities:

   1. Maintain a cache of resized images to serve
   2. Select an appropriate worker to take advantage of the fetched image
      cache.

The worker processes speak HTTP and handle the fetching and resizing of
the images. The master process does some sort of hashing (currently crc32)
to determine which worker to ask for the full size image. The full size
image is cached, it is resized/cropped and then processed image is sent.

All processes are using an event loop (libevent with tornado) to handle
the I/O. Since image resizing is not asynchronous, the workers can block
for a short amount of time, though in practice, these operations are very
quick. The main process doesn't block at all, as it does only I/O.

### Resizing

By design, phizer does not allow you to resize to arbitrary sizes. Instead,
it is configured to use a set of predefined sizes. Why such a constraint?
Quite frankly, too much choice leads to poor performance. Suppose a 
designer says, "we should make this 2 pixels bigger," and the image tags
get updated--now we're missing the cache on every request.

### Fetching -- Backends

We separate image source locations into two categories--masters and slaves.
Currently, phizer supports having one master, and multiple slaves. 

* master: This should be the main source of images. In our use cases, this
  is Amazon S3
* slaves: This should be a secondary source of images. In our case, it's our
  local web servers where images are uploaded, but aren't necessarily synced
  to S3 yet. Slaves, as currently implemented randomly queries, though
  we *should* request to all slaves in parallel.
  
As currently implemented, phizer doesn't do failover to slaves should the
master be unavailable. This is because it doesn't fit our use case. Our
system is setup to delete uploaded images from disk after a short timeout 
(30s) as soon as they are successfully copied to S3.


### URL format

URLs in use are fairly straightforward:
 
* Resizing only

    /(width)x(height)/path.ext
    
* Resizing with cropping points.

    # tl = top-left, br = bottom-right
    /(width)x(height)/(tl-x)x(tl-y)/(br-x)x(br-y)/path.ext
 
That's it. `path.ext` is requested from a master or one of the slaves.

## A note on logging

The ideal situation is that phizer can log to syslog. Unfortunately, this
currently can't work since under tornado, we'd need to incorporate the I/O
into the IOLoop. As a result, for now, all logging calls write to stdio.

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
