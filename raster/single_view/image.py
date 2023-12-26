# -*- coding: utf-8 -*-

from mochila import plog

import cv2 as cv
import numpy as np


def rectify(orig_image_bounds,
            georef_image_verts,
            rows,
            cols,
            utf8_path, *,
            verbose=True):
    """Create an homography rectified array from image in utf8_path.
    -----
    Params:
        rows:      int
            Number of rows in new array.
        cols:       int
            Number of columns in new arraw.
        utf8_path:  str
            Path to original image file.
        verbose:    bool (optional, keyword only)
            Control if print some information or not.
            Defaults to True.
    -----
    Returns:
        georef_image_array: ndarray
            Array with (bands, rows, columns) shape and 4 (rgba) bands.
    """

    h_matrix = cv.getPerspectiveTransform(np.float32(orig_image_bounds),
                                        np.float32(georef_image_verts))
    if verbose:
        plog(f'{h_matrix = }')

    img = cv.imread(utf8_path)
    rgba = cv.cvtColor(img, cv.COLOR_RGB2RGBA)
    if verbose:
        plog(f'{rgba.shape = }')

    georef_image_array = cv.warpPerspective(rgba,
                                            h_matrix,
                                            [cols, rows])


    if verbose:
        plog(f'{type(georef_image_array) = }')
        plog(f'{georef_image_array.shape = }')

    cv.imwrite(utf8_path[:-4]+'_rectified.PNG', georef_image_array)
    return georef_image_array
