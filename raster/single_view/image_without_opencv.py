# -*- coding: utf-8 -*-

from osgeo import gdal
gdal.UseExceptions()

import numpy as np

from mochila import plog
from mochila.utils import gdal_utils
from mochila.raster.single_view import homography





def create(orig_image_bounds,
            georef_image_verts,
            rows,
            cols,
            utf8_path, *,
            verbose=True):
    """Create an homography reprojected array from image in utf8_path.
    -----
    Params:
        rows:      int
            Number of rows in new array.
        cols:       int
            Number of columns in new arraw.
        h_matrix:   list
            Homography 3x3 matrix to convert from reprojected to
             original rowcol coordinates.
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

    orig_image_array = gdal_utils.get_image_array(utf8_path)
    orig_bands, orig_rows, orig_cols = np.shape(orig_image_array)

    # Transformation from dest to src to compute the src position of dest pixels
    h_matrix = homography.find(georef_image_verts, orig_image_bounds)[0]
    if verbose:
        plog(f'{h_matrix = }')

    georef_image_array = np.zeros((4, rows, cols), dtype=np.uint8)

    for row in range(rows):
        row_coord = row + 0.5
        for col in range(cols):
            col_coord = col + 0.5

            georef_pixel = [row_coord, col_coord]
            orig_pixel = homography.apply(georef_pixel, h_matrix)
            orig_row, orig_col = np.floor(orig_pixel)

            # Write the values only if there is a valid origin pixel coordinate
            if (orig_row >= 0 and
                orig_row <  orig_rows and
                orig_col >= 0 and
                orig_col < orig_cols):
                    georef_image_array[0:3, row, col] = orig_image_array[0:3, int(orig_row), int(orig_col)]
                    georef_image_array[3, row, col] = 255

    return georef_image_array
