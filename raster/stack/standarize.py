# -*- coding: utf-8 -*-

from puentes.plugin import plog

import numpy as np
import rasterio
from rasterio import merge
from mochila.utils import numpy_utils


def merge_tiles(datasets, dst_path):
    """Merge in one raster all source datasets.

    datasets: List of Path-like objects of source raster tiles.
    dst_path: Path-like object for destination raster.
    """
    plog(f'(merge_tiles) Writing: {str(dst_path)}.')
    merge.merge(datasets, dst_path=dst_path)

def compute_statistics(src_path, n_band):
    """Computar estadísticas de una banda de un raster, para normalizarla.

    Parameters:
        src_path: PathLike. Path to the source raster file.
        n_band: Int. Number of band to compute statistics.
        dst_path: PathLike. Path to destination text file to store stats.

    Returns:
        Dict. Stats (mean, median, std, p5, p95) of raster band.
    """
    plog(f'(compute_statistics) Reading: {src_path}.')
    with rasterio.open(src_path) as src:
        # Dictionary with {band_n: (data_type, nodata_value)} elements
        props = {prop[0]: prop[1] for prop in zip(src.indexes, src.nodatavals)}
        arr_band = src.read(n_band)

    nodata = props[n_band]
    mean, median, std, p5, p95 = numpy_utils.get_band_statistics(arr_band, nodata)
    stats = dict(
        mean = mean,
        median = median,
        std = std,
        p5 = p5,
        p95 = p95
    )
    return stats

def standarize(src_path, n_band, dst_path, dst_dtype, dst_nodata, t, s):
    """standarize a band and write it to disk.

    Parameters:
        src_path:   PathLike. Path to the source raster file.
        n_band:     Int. Number of band to normalize.
        dst_path:   PathLike. Path to destination normalized raster band.
        dst_dtype:  rasterio.dtype. Datatype for destination raster band.
        dst_nodata: Int or Float. Destination nodata value.
        t:          Float. Translation.
        s:          Float. Scale.

    Returns:
        Dict. Stats (mean, median, std, p5, p95) of raster band.
    """
    with rasterio.open(src_path) as src:
        arr_band = src.read(n_band)
        kwargs = src.meta
        # Dictionary with {band_n: (data_type, nodata_value)} elements
        props = {prop[0]: prop[1] for prop in zip(src.indexes, src.nodatavals)}

    arr = arr_band.astype('float64')
    nodata = props[n_band]

    plog(f'{t = }')
    plog(f'{s = }')

    # Standarized values (first translate, then scale).
    standarized = np.where(
        arr==nodata,
        dst_nodata,
        (arr + t) * s
    )
    # Clip to the min and max values of the dtype (only for integer types)
    np.clip(standarized, np.iinfo(dst_dtype).min, np.iinfo(dst_dtype).max, standarized)

    # Set metadata datatype as Float32, one band, and nodata value
    kwargs['dtype'] = dst_dtype
    kwargs['count'] = 1
    kwargs['nodata'] = dst_nodata

    # Create the file.
    plog(f'(normalize) Writing: {dst_path}.')
    with rasterio.open(dst_path, 'w', **kwargs) as dst:
        dst.write_band(1, standarized.astype(dst_dtype))
