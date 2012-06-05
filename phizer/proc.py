"""resizer.py 

functions for resizing an instance of PIL.Image
"""
try:
    import Image
except ImportError:
    from PIL import Image

import constraints
import logging

def resize(config, image, width=None, height=None, algorithm=None, **kwargs):
    """Resize image to the specs provided in `props`

    props contains:
      width, height
    """
    size = image.size
    # TODO: config max dimension
    if width >= 1500 or height >= 1500:
        return image

    if width == size[0] and height == size[1]:
        # nothing to futz with
        return image

    steps = constrain(size[0], size[1], width, height, algorithm)

    logging.debug("Steps: %s" % steps)

    for step in steps:
        if step[0] == 'center':
            # put image on canvas of config.color of width and height
            logging.debug('centering image: on (%d, %d) canvas' % (width, height))
            image = center_image(config, image, width, height, step[1], step[2])
        if step[0] == 'scale':
            logging.debug('scaling to: %s\n' % (step[1],))
            image.thumbnail(step[1], Image.ANTIALIAS)
        elif step[0] == 'crop':
            logging.debug('crop to: %s\n' % (step[1],))
            image = image.crop(step[1])
    return image

def center_image(config, image, width, height, topx, topy):
    blank = Image.new("RGB", (width, height), config.canvas_color)
    box = (topx, topy)
    blank.paste(image, box)
    return blank

def crop(config, image, topx=None, topy=None, botx=None, boty=None, **kwargs):
    """Crops image based on properties
    
    crop points represent ratios. So, if the image is 1024x768, and you want
    the a 500x500 pixel image from the center, the crop points would be:

      256x174/744x826.


    Why is this? Because we want 3 significant digits for the ratio without 
    the annoying noise in the url. 
    """
    if not (topx and topy and botx and boty):
        return image

    size = image.size

    tx = int(size[0]/1000.0 * int(topx))
    ty = int(size[1]/1000.0 * int(topy))

    bx = int(size[0]/1000.0 * int(botx))
    by = int(size[1]/1000.0 * int(boty))


    logging.debug('crop has size: %s. top: (%d, %d), bottom: (%d, %d)' 
                  ' -> to points top: (%d, %d), bottom: (%d, %d))' % \
                      (size, topx, topy, botx, boty, tx, ty, bx, by))

    # OK, possible to crop now.
    return image.crop((tx, ty, bx, by))


def constrain(from_width, from_height, to_width, to_height, algorithm):
    """Given from dimensions and target dimensions, determine the
    box that fits within towidth/toheight optimally without spilling
    over, but allowing a centered crop.

    Call the appropriate function to handle the given algorithm, or default
    to function
    """
    algorithm = getattr(constraints, 'constrain_%s' % algorithm)
    if algorithm:
        return algorithm(from_width, from_height, to_width, to_height)
    else:
        return constraints.constrain_max(from_width, from_height, to_width, to_height)
