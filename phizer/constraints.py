import math
import logging


def constrain_square(fw, fh, tw, th):
    """Generates steps to make a square out of the source and target
    dimensions.

    Ensures that steps always produce a square, but the square may be
    smaller than the target dimensions depending on the source size
    """
    steps = []
    
    # if it's a square, then we're going to be square regardless.
    tw = max(tw, th)
    th = tw

    if tw > fw or th > fh:
        # one of the dimensions isn't large enough, so we'll scale it
        tw = min(fw, fh)
        th = tw

    # crop to square and scale to (tw, th)
    diff = fw - fh
    if diff > 0: # landscape
        extra = diff / 2
        steps.append(('crop', (extra, 0, fw - extra, fh)))
    elif diff < 0: # portrait
        extra = abs(diff / 2)
        steps.append(('crop', (0, extra, fw, fh - extra)))

    steps.append(('scale', (tw, th)))
    return steps

def constrain_portrait(fw, fh, tw, th):
    """Generates steps to make a portrait out of the source and target
    dimensions.

    Ensures that steps always produce a portrait, but the portrait may
    be smaller than the target dimensions depending on the source size
    """
    if tw > fw or th > fh:
        return _crop_and_keep(fw, fh, tw, th)

    steps = []

    ratio_h = th / float(fh)
    inter_height = th
    inter_width = int(ratio_h * fw)

    steps.append(('scale', (inter_width, inter_height)))
    
    if inter_width > tw:
        tw = int(tw * ratio_h)
        wdiff = inter_width - tw
        steps.append(('crop', (abs(wdiff/2), 0, 
                               inter_width - abs(wdiff/2), inter_height)))

    return steps


def constrain_landscape(fw, fh, tw, th):
    """Generates steps to make a landscape out of the source and target
    dimensions.

    Ensures that steps always produce a landscape, but the portrait may
    be smaller than the target dimensions depending on the source size
    """
    if tw > fw or th > fh:
        return _crop_and_keep(fw, fh, tw, th)

    steps = []

    ratio_w = tw / float(fw)
    inter_width = tw
    inter_height = int(ratio_w * fh)

    steps.append(('scale', (inter_width, inter_height)))

    if inter_height > th:
        th = int(th * ratio_w)
        hdiff = inter_height - th
        steps.append(('crop', (0, abs(hdiff/2), 
                               inter_width, inter_height - abs(hdiff/2))))

    return steps

def constrain_max(fw, fh, tw, th):
    if fw == fh:
        return constrain_square(fw, fh, tw, th)
    frls = (fw - fh) > 0    
    if frls:
        return constrain_landscape(fw, fh, tw, th)
    else:
        return constrain_portrait(fw, fh, tw, th)


def _crop_and_keep(fw, fh, tw, th):
    wd = fw - tw
    hd = fh - th

    tx = 0
    ty = 0
    bx = fw
    by = fh

#    import pdb
#    pdb.set_trace()

    if wd > 0:
        # crop horizontally
        tx += (wd / 2) 
        bx -= (wd / 2)

    if hd > 0:
        # crop vertically
        ty += (hd / 2) 
        by -= (hd / 2)

    return [('crop', (tx, ty, bx, by))]
