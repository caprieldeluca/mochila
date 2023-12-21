# -*- coding: utf-8 -*-

from mochila import plog
from mochila.vector import vlayers
from mochila.raster.single_view import (
    boundingbox,
    homography,
    metadata,
    projs,
    transformations
)

import numpy as np

# Sensors width in mm (https://www.djzphoto.com/blog/2018/12/5/dji-drone-quick-specs-amp-comparison-page)
SENSOR_WIDTHS = {
    'DJI': {
        'FC7303': 6.3 # Mini 2
    }
}


PRINTS = True




def process(utf8_path, corrections):
    """Get relevant data of image by processing its metadata."""

    tags = metadata.get_tags(utf8_path)

    maker, model = metadata.get_mm(tags)

    # Get number of Rows and Cols of image
    rows, cols = metadata.get_rowscols(tags, maker, model)

    sensor_width = SENSOR_WIDTHS[maker][model] / 1000 # m
    pixel_size = sensor_width / cols # m/px

    focal_length = tags['Exif.Photo.FocalLength'] / 1000 # m
    plog(f'{focal_length = }')

    if PRINTS:
        plog(f'{rows = }')
        plog(f'{cols = }')
        plog(f'{pixel_size = } m/px')


    # Define bounds in image coordinates
    image_bounds = [
        [0, 0],
        [rows, 0],
        [rows, cols],
        [0, cols]
    ]

    # Convert from image (row, col) to oblique camera (front, right, down) coordinates
    converter = transformations.i2o_converter(rows, cols, pixel_size, focal_length)
    oblique_bounds = [converter(coord) for coord in image_bounds]
    plog(f'{oblique_bounds = }')

    # Convert from oblique (front, right, down) to vertical (x, y, z) coordinates
    rpy = np.array(metadata.get_rpy(tags, maker, model))
    deltas_rpy = np.array([
        corrections['DELTA_ROLL'],
        corrections['DELTA_PITCH'],
        corrections['DELTA_YAW']
    ])
    rpy = rpy + deltas_rpy

    plog(f'{rpy = }')
    converter = transformations.o2v_converter(rpy)
    vertical_bounds = [converter(coord) for coord in oblique_bounds]
    vertical_bounds.append(np.array([0,0,focal_length]))
    plog(f'{vertical_bounds = }')

    # Convert from vertical to topocentric plane coordinates
    alt = metadata.get_altitude(tags, maker, model)
    alt = alt + corrections['DELTA_ALT']
    converter = transformations.v2t_converter(alt)
    enu_bounds = [converter(coord) for coord in vertical_bounds]
    plog(f'{enu_bounds = }')

    # Convert from topocentric plane coordinates to utm
    lat, lon = metadata.get_latlon(tags, maker, model)

    # Create a layer of points with the vertices of the image
    crs = f'PROJ:+proj=nsper +h={alt} +lat_0={lat} +lon_0={lon} +datum=WGS84 +type=crs'
    vlayers.create_layer_from_points(enu_bounds, crs)

    # Get the bounding box of the image rectified in topocentric coordinates
    bbox = boundingbox.get_bbox(enu_bounds)
    plog(f'{bbox = }')

