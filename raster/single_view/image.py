# -*- coding: utf-8 -*-

from osgeo import gdal


def get_image_array(utf8_path):
    """Get a numpy array from an image file."""

    ds = gdal.Open(utf8_path, gdal.GA_ReadOnly)
    if not ds:
        raise Exception(f"Can't open {utf8_path} as a GDAL dataset.")

    array = ds.ReadAsArray()

    return array

def create_reprojected_array(rows, cols, h_matrix, utf8_path):
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
    -----
    Returns:
        georef_image_array: ndarray
            Array with (band, row, column) shape and 4 (rgba) bands.
    """
    pass