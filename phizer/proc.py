"""resizer.py 

functions for resizing an instance of PIL.Image
"""

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

    for step in steps:
        if step[0] == 'scale':
            print 'scaling to: %s\n' % (step[1],)
            image.thumbnail(step[1], Image.ANTIALIAS)
        elif step[0] == 'crop':
            print 'crop to: %s\n' % (step[1],)
            image = image.crop(step[1])
    return image


def crop(config, image, topx=None, topy=None, botx=None, boty=None, **kwargs):
    """Crops image based on properties
    """
    return image


def constrain(from_width, from_height, to_width, to_height):
    """Given from dimensions and target dimensions, determine the
    box that fits within towidth/toheight optimally without spilling
    over, but allowing a centered crop.
    """
    from_ratio = float(from_width) / from_height
    to_ratio = float(to_width) / to_height

    if from_ratio == to_ratio:
        # simple scaling. allow scales greater, even if the quality is worse
        return [('scale', to_width, to_height)]
    elif to_ratio == 1.0: # square
        return _to_sq(from_width, from_height, to_width, to_height)
    else:
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
    if fw < fh and tw < th: # portrait -> portrait, keep height
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

