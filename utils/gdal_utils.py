# -*- coding: utf-8 -*-

from mochila import plog

from osgeo import (
    gdal,
    gdal_array,
    osr
)
import numpy as np


def get_image_array(utf8_path):
    """Get a numpy array from an image file."""

    ds = gdal.Open(utf8_path, gdal.GA_ReadOnly)
    if not ds:
        raise Exception(f"Can't open {utf8_path} as a GDAL dataset.")

    array = ds.ReadAsArray()

    return array

def array2ds(utf8_path, array, geotrans, crs, *, verbose=True):
    """Create a GDAL dataset from a numpy array.
    -----
    Params:
        array:          ndarray
            Numpy array to create the dataset.
        geotrans:       list
            List of geotransformation array parameters.
            (https://gdal.org/tutorials/geotransforms_tut.html)
        crs:            str
            Coordinate Reference System to be assigned to dataset.
        verbose:        bool (optional, keyword only)
            Control if print some information or not.
            Defaults to True.
    -----
    Returns:
        ds:             dataset
            Dataset GDAL object.
    """

    driver = gdal.GetDriverByName("GTiff")

    ysize, xsize, bands = array.shape
    ds = driver.Create(utf8_path, xsize, ysize, bands, gdal.GDT_Byte)

    ds.SetGeoTransform(geotrans)

    # Define the format of the crs
    crs_format, crs_def = crs.split(':')

    spat_ref = osr.SpatialReference()
    if crs_format == 'PROJ':
        spat_ref.ImportFromProj4(crs_def)

    wkt = spat_ref.ExportToWkt()
    ds.SetProjection(wkt)

    ds.WriteArray(np.moveaxis(array, -1, 0))

    plog(f'{ds.GetGeoTransform() = }')
    plog(f'{ds.GetSpatialRef().ExportToWkt() = }')
    ds.FlushCache()
    return ds


def write_ds(utf8_path, ds):
    """Write a GDAL dataset to disk."""
