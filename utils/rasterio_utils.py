# -*- coding: utf-8 -*-
from mochila import plog
from mochila.utils import pathlib_utils

import numpy as np
import rasterio
# https://rasterio.readthedocs.io/en/stable/api/index.html

def get_raster_info(utf8_path):
    # Read info from source raster.
    with rasterio.open(utf8_path) as src:
        plog(f'{src.meta = }')


def extract_bands(src_path, src_bands, dst_path, dst_bands):
    """Exctract bands to new files.

    src_path: Path-like object to source raster file.
    src_bands: Dictionary of {'band_name': band_number} elements
        with the source bands to extract.
    dst_path: Path-like object to destination file.
    dst_bands: Dictionary of {'band_name': band_number} elements
        with the destination bands.

    Return:
        extracted_paths: List of paths extracted.
    """
    with rasterio.open(src_path) as src:
        kwargs = src.meta
        # Update metada for destination file, will record just one band
        kwargs['count'] = 1
        extracted_paths = {}
        for b_name, b_number in src_bands.items():
            new_stem = '_' + str(dst_bands[b_name]) + b_name
            new_path = pathlib_utils.append_stem(dst_path, new_stem)

            plog(f'(extract_bands) Writing: {str(new_path)}.')
            with rasterio.open(new_path, 'w', **kwargs) as dst:
                arr = src.read(b_number)
                dst.write_band(1, arr)
                extracted_paths[b_name] = new_path

    return extracted_paths


