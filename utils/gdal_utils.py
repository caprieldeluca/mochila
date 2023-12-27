# -*- coding: utf-8 -*-

import os

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

def array2ds(array, geotrans, crs, *, verbose=True):
    """Create a memory GDAL dataset from a numpy array.
    -----
    Params:
        array:          ndarray
                Numpy array to create the dataset.
        geotrans:       list
                List of geotransformation array parameters.
                (https://gdal.org/tutorials/geotransforms_tut.html)
        crs:            str
                Coordinate Reference System to be assigned to dataset.
                Any string accepted by OGRSpatialReference.SetFromUserInput().
        verbose:        bool (optional, keyword only)
                Control if print some information or not.
                Defaults to True.
    -----
    Returns:
        ds:             dataset
                Dataset GDAL object.
    """

    driver = gdal.GetDriverByName("MEM")

    ysize, xsize, bands = array.shape
    ds = driver.Create("", xsize, ysize, bands, gdal.GDT_Byte)

    ds.SetGeoTransform(geotrans)

    spat_ref = osr.SpatialReference()
    spat_ref.SetFromUserInput(crs)

    wkt = spat_ref.ExportToWkt()
    ds.SetProjection(wkt)

    ds.WriteArray(np.moveaxis(array, -1, 0))

    if verbose:
        plog(f'{ds.ReadAsArray().shape = }')

    return ds


def warp_ds(utf8_path, ds, dst_crs, *, verbose=True):
    """Warp a GDAL dataset and write it to disk.
    -----
    Params:
        utf8_path:      str
                Path to store the warped image.
        ds:             GDAL dataset
                The dataset (with src and geotransform) to be warped and saved.
        dst_crs:        str
                Destination Spatial Reference System to project to the source dataset.
                Any string accepted by OGRSpatialReference.SetFromUserInput().
        verbose:        bool (optional, keyword only)
                Control if print some information or not.
                Defaults to True.
    -----
    Returns:
        dst_ds:         GDAL dataset
                The warped dataset.
    """

    # Ensure the path exists
    dirname = os.path.dirname(utf8_path)
    if not os.path.exists(dirname):
        plog(f"'{dirname}' directory does not exist and will be created.")
        os.makedirs(dirname)

    creation_options = ['COMPRESS=JPEG', 'PHOTOMETRIC=RGB']
    warp_options = {
        'format': 'GTiff',
        'dstSRS': dst_crs,
        'resampleAlg': 'bilinear',
        'srcAlpha': True,
        'dstAlpha': True,
        'creationOptions': creation_options
    }

    dst_ds = gdal.Warp(utf8_path, ds, **warp_options)
    if verbose:
        plog(f'{utf8_path = }')

    return dst_ds

