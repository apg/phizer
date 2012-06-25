import math
import logging


def constrain_square(fw, fh, tw, th):
    """Generates steps to make a square out of the source and target
    dimensions. 

    1. crop to a square
    2. if target is smaller than source, shrink it
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
    
    # scale never scales up (only down), so this would work ok even if we unconditionly append 'scale'.
    if target_size < fh or target_size < fw:
        steps.append(('scale', (target_size, target_size)))
    return steps

def constrain_max(fw, fh, tw, th):
    """Generates steps to scale down the image, as long as it fits within tw x th rectangle.
    """
    
    logging.debug("at constrain max: %dx%d => %dx%d" % (fw,fh,tw,th))
    steps = [('scale', (tw, th))]
    return steps

def constrain_portrait(fw, fh, tw, th):
    """Generates steps to make a portrait out of the source and target
    dimensions.
    May crop sides of a wide image, will never crop top or bottom.

    1. If image is taller than target, scale down
    2. If image is too wide, crop sides
    """

    if fw <= tw and fh <= th:
        return []

    steps = []
    scale_ratio = float(th) / fh
    if scale_ratio > 1.0:
        # no need to scale down
        inter_height = fh
        inter_width = fw
    else:
        inter_height = th
        inter_width = int(fw * scale_ratio)
        steps.append(('scale', (inter_width, inter_height)))

    crop_width = inter_width - tw
    if crop_width > 0:
        delta = int(crop_width / 2)
        steps.append(('crop', (delta, 0, inter_width - delta, inter_height)))

    return steps


def constrain_landscape(fw, fh, tw, th):
    """Generates steps to make a landscape out of the source and target
    dimensions.
    May crop top&bottom of a tall image, will never crop sides.

    1. If image is wider than target, scale down
    2. If image is too high, crop top and bottom
    """

    if fw <= tw and fh <= th:
        return []

    steps = []
    scale_ratio = float(tw)/fw
    if scale_ratio > 1.0:
        # no need to scale down
        inter_height = fh
        inter_width = fw
    else:
        inter_width = tw
        inter_height = int(fh * scale_ratio)
        steps.append(('scale', (inter_width, inter_height)))

    crop_height = inter_height - th
    if crop_height > 0:
        delta = int(crop_height / 2)
        steps.append(('crop', (0, delta, inter_width, inter_height - delta)))

    return steps

