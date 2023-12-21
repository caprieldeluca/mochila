# -*- coding: utf-8 -*-

from osgeo import gdal


def get_image_array(utf8_path):
    """Get a numpy array from an image file."""

    ds = gdal.Open(utf8_path, gdal.GA_ReadOnly)
    if not ds:
        raise Exception(f"Can't open {utf8_path} as a GDAL dataset.")

    array = ds.ReadAsArray()

    return array
