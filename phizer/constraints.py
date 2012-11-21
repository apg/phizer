import math
import logging


def constrain_square(fw, fh, tw, th):
    """Generates steps to make a square out of the source and target
    dimensions. If somehow target is not a square, increase it to be such.

    1. crop to a square
    2. resize it to fit the target
    """
    steps = []
    
    # crop to square
    extra_width = fw - fh
    crop = abs(extra_width / 2)
    if extra_width > 0: # landscape
        steps.append(('crop', (crop, 0, fw - crop, fh)))
    elif extra_width < 0: # portrait
        steps.append(('crop', (0, crop, fw, fh - crop)))

    # target should always be square
    target_size = max(tw,th)
    
    # resize would scale up
    steps.append(('resize', (target_size, target_size)))

    return steps

def constrain_max(fw, fh, tw, th):
    """Generates steps to scale down the image, as long as it fits within tw x th rectangle.
    """
    scalex = float(tw)/fw
    scaley = float(th)/fh
    scale = min(scalex,scaley)
    inter_w = int(scale * fw)
    inter_h = int(scale * fh)
    steps = [('resize', (inter_w, inter_h))]
    return steps

def constrain_portrait(fw, fh, tw, th):
    """Generates steps to make a portrait out of the source and target
    dimensions.
    May crop sides of a wide image, will never crop top or bottom.

    1. Resize the image such that height fits target height
    2. If image is too wide, crop sides
    """

    steps = []
    scaley = float(th)/fh

    inter_height = th
    inter_width = int(fw * scaley)
    steps.append(('resize', (inter_width, inter_height)))

    crop_width = inter_width - tw
    if crop_width > 0:
        delta = int(crop_width / 2)
        steps.append(('crop', (delta, 0, inter_width - delta, inter_height)))

    return steps


def constrain_landscape(fw, fh, tw, th):
    """Generates steps to make a landscape out of the source and target
    dimensions.
    May crop top&bottom of a tall image, will never crop sides.

    1. Resize the image such that width fits target width
    2. If image is too high, crop top and bottom
    """

    steps = []
    scalex = float(tw)/fw
    inter_width = tw
    inter_height = int(fh * scalex)
    steps.append(('resize', (inter_width, inter_height)))

    crop_height = inter_height - th
    if crop_height > 0:
        delta = int(crop_height / 2)
        steps.append(('crop', (0, delta, inter_width, inter_height - delta)))

    return steps

