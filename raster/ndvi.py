# -*- coding: utf-8 -*-

from puentes.plugin import plog
from mochila.utils import pathlib_utils
import numpy as np
import rasterio
from pathlib import Path


def compute_ndvi(src_path, red_band_n, nir_band_n, dst_path, dst_nodata):
    """Compute NDVI for a raster band"""

    # Read input file
    with rasterio.open(src_path) as src:
        red_band = src.read(red_band_n)
        nir_band = src.read(nir_band_n)
        kwargs = src.meta
        nodatavals = src.nodatavals

    # Convert to float64
    red = red_band.astype('float64')
    nir = nir_band.astype('float64')

    # nodatavals is a list of nodata values, indexed from 0
    #  (bands numbers are indexed from 1)
    red_nodata = nodatavals[red_band_n - 1]
    nir_nodata = nodatavals[nir_band_n - 1]

    # Allow division by zero
    np.seterr(divide='ignore', invalid='ignore')

    # Compute NDVI
    ndvi = np.where(
        np.logical_or(red==red_nodata, nir==nir_nodata),
        dst_nodata,
        (nir - red) / (nir + red)
    )

    # Set metadata datatype as Float32, one band, and nodata value
    kwargs['dtype'] = rasterio.float32
    kwargs['count'] = 1
    kwargs['nodata'] = dst_nodata

    # Create the file.
    plog(f'(compute_ndvi) Writing: {dst_path}.')
    with rasterio.open(dst_path, 'w', **kwargs) as dst:
        dst.write_band(1, ndvi.astype(rasterio.float32))

