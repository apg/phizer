"""resizer.py 

functions for resizing an instance of PIL.Image
"""
try:
    import Image
except ImportError:
    from PIL import Image

import logging


def resize(config, image, width=None, height=None, **kwargs):
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

    steps = constrain(size[0], size[1], width, height)

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


def constrain(from_width, from_height, to_width, to_height):
    """Given from dimensions and target dimensions, determine the
    box that fits within towidth/toheight optimally without spilling
    over, but allowing a centered crop.
    """
    from_ratio = float(from_width) / from_height
    to_ratio = float(to_width) / to_height

    exceeds_y = from_height > to_height
    exceeds_x = from_width > to_width

    logging.debug('from_ratio: %f, to_ratio: %f' % (from_ratio, to_ratio))

    if exceeds_y or exceeds_x:
        if from_ratio == to_ratio:
            # simple scaling. allow scales greater, even if the quality is worse
            return [('scale', (to_width, to_height))]
        elif to_ratio == 1.0: # square
            return _to_sq(from_width, from_height, to_width, to_height)
        else:
            return _to_rect(from_width, from_height, to_width, to_height)
    else: # incomplete
        logging.debug("doesn't exceed in either direction")
        return _to_rect(from_width, from_height, to_width, to_height)

def _to_sq(fw, fh, tw, th):
    func = None
    if fw < fh: # portrait
        func = _resize_keep_width
    else: # landscape
        func = _resize_keep_height
    return func(fw, fh, tw, th)


def _to_rect(fw, fh, tw, th):
    # constrain to max of th, tr
    func = None
    if fw < tw and fh < th:
        func = _center_and_keep
    elif fw < fh and tw < th: # portrait -> portrait, keep height
        func = _resize_keep_height
    elif fw < fh: # portrait -> landscape, keep width
        func = _resize_keep_width
    elif fw > fh and tw > th: # landscape -> landscape, keep width
        func = _resize_keep_width
    else: # landscape -> portrait, keep height
        func = _resize_keep_height
    return func(fw, fh, tw, th)


def _resize_keep_height(fw, fh, tw, th):
    ratio_h = th / float(fh)
    inter_width = ratio_h * fw
    inter_height = th
    wdiff = inter_width - tw
    return [('scale', (int(inter_width), int(inter_height))),
            ('crop', (int(wdiff/2), 0, int(inter_width - (wdiff/2)), th))]

def _resize_keep_width(fw, fh, tw, th):                 
    ratio_w = tw / float(fw)
    inter_width = tw
    inter_height = ratio_w * fh
    hdiff = inter_height - th
    return [('scale', (int(inter_width), int(inter_height))),
            ('crop', (0, int(hdiff/2.0), tw, int(inter_height - (hdiff/2))))]

def _center_and_keep(fw, fh, tw, th):
    topx = int((tw - fw) / 2)
    topy = int((th - fh) / 2)
    return [('center', topx, topy)]

