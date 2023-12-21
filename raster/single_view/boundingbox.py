# -*- coding: utf-8 -*-

from mochila import plog
import numpy as np


def get_bbox(points):
    """Get the list of bounding box vertices from points coordinates.

    -----
    Params:
        points:     List of [x, y] coordinates of points.
    -----
    Return:
        bbox:       List of bounding box vertices (lower-left and upper-right) coordinates.
                        [xmin, ymin, xmax, ymax]
    """

    x = np.array(points)[:, 0]
    xmin = x.min()
    xmax = x.max()

    y = np.array(points)[:, 1]
    ymin = y.min()
    ymax = y.max()

    bbox = [xmin, ymin, xmax, ymax]

    return bbox
