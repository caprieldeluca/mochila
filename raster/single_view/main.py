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

# Corrections to sensor metadata values
CORRECTIONS = {
    'DELTA_ROLL': 0.0,
    'DELTA_PITCH': 0.0,
    'DELTA_YAW': 0.0,
    'DELTA_ALT': 0.0
}



def _verify_corrections(corrections):
    """Verify that al corrections are present or assign default values.
    -----
    Paramters:
        corrections: dict
                Corrections to sensor values.
    -----
    Return:
        corrections: dict
    """

    if 'DELTA_ROLL' not in corrections.keys() or not isinstance(corrections['DELTA_ROLL'], (int, float)):
        plog("DELTA_ROLL key absent or value not recognized in corrections, defaults to 0.0.")
        corrections['DELTA_ROLL'] = 0.0
    if 'DELTA_PITCH' not in corrections.keys() or not isinstance(corrections['DELTA_PITCH'], (int, float)):
        plog("DELTA_PITCH key absent or value not recognized in corrections, defaults to 0.0.")
        corrections['DELTA_PITCH'] = 0.0
    if 'DELTA_YAW' not in corrections.keys() or not isinstance(corrections['DELTA_YAW'], (int, float)):
        plog("DELTA_YAW key absent or value not recognized in corrections, defaults to 0.0.")
        corrections['DELTA_YAW'] = 0.0
    if 'DELTA_ALT' not in corrections.keys() or not isinstance(corrections['DELTA_ALT'], (int, float)):
        plog("DELTA_ALT key absent or value not recognized in corrections, defaults to 0.0.")
        corrections['DELTA_ALT'] = 0.0

    return corrections



def process(utf8_path,
            corrections=CORRECTIONS, *,
            gsd = 0.0,
            sensor_widths=SENSOR_WIDTHS,
            with_opencv=True,
            verbose=True):
    """Process the georeference of a single-view perspective image.
    -----
    Parameters:
        uft8_path:      str
                Path to image file.
        corrections:    dict (optional)
                Dictionary with corrections for sensor angles values and altitude.
                    Sensor angles are Roll ('DELTA_ROLL' key), Pitch ('DELTA_PITCH' key)
                     and Yaw ('DELTA_YAW' key) in decimal degrees. Altitude is
                     in meters. All corrections are optional.
                Defaults to all corrections to zero.
        gsd:            float
                Force the rectification to this gsd, in meters.
                If zero, it is computed from image metadata values.
                Defaults to 0.0.
        sensor_widths:  dict (optional, keyword only)
                Dictionary with sensor maker, model and width (in millimeters).
                    The width value will be extracted using maker and model present
                     in image metadata tags.
                Example: {'DJI': {'FC7303': 6.3}}
                Defaults to a dictionary of some makers and models already tested.
        with_opencv:    bool (optional, keyword only)
                Use OpenCV to transform the image. If false, a less efficient
                 NumPy based solution is implemented.
                Defaults to True.
        verbose:        bool (optional, keyword only)
                Control if print some information or not.
                Defaults to True.
    Return:
        georef_path:    str
                Path to georeferenced image file.
    """

    corrections = _verify_corrections(corrections)

    tags = metadata.get_tags(utf8_path)

    maker, model = metadata.get_makermodel(tags)

    # Get number of Rows and Cols of image
    rows, cols = metadata.get_rowscols(tags, maker, model)

    try:
        sensor_width = sensor_widths[maker][model] / 1000 # m
    except KeyError as e:
        plog(f"Maker '{maker}' and/or Model '{model}' not implemented in sensor widths:",
            [(maker, list(sensor_widths[maker].keys())) for maker in sensor_widths.keys()])
        raise e

    pixel_size = sensor_width / cols # m/px

    focal_length = tags['Exif.Photo.FocalLength'] / 1000 # m
    if verbose:
        plog(f'{focal_length = }')

    if verbose:
        plog(f'{rows = }')
        plog(f'{cols = }')
        plog(f'{pixel_size = } m/px')


    # Define bounds in image coordinates (center of top-left pixel is zero)
    # x to cols, y to rows
    orig_image_bounds = np.array([
        [-0.5, -0.5],
        [cols - 0.5, -0.5],
        [cols - 0.5, rows - 0.5],
        [-0.5, rows - 0.5]
    ])
    if verbose:
        plog(f'{orig_image_bounds = }')

    # Convert from image (row, col) to oblique camera (front, right, down) coordinates
    i2o_conv = transformations.i2o_converter(rows, cols, pixel_size, focal_length)
    oblique_verts = [i2o_conv(coord) for coord in orig_image_bounds]
    if verbose:
        plog(f'{oblique_verts = }')

    # Convert from oblique (front, right, down) to vertical (x, y, z) coordinates
    rpy = np.array(metadata.get_rpy(tags, maker, model))
    deltas_rpy = np.array([
        corrections['DELTA_ROLL'],
        corrections['DELTA_PITCH'],
        corrections['DELTA_YAW']
    ])
    rpy = rpy + deltas_rpy
    if verbose:
        plog(f'{rpy = }')
    o2v_conv = transformations.o2v_converter(rpy)
    vertical_verts = [o2v_conv(point) for point in oblique_verts]
    if verbose:
        plog(f'{vertical_verts = }')


    # Convert from vertical to topocentric plane coordinates
    alt = metadata.get_altitude(tags, maker, model)
    alt = alt + corrections['DELTA_ALT']
    v2t_conv = transformations.v2t_converter(alt)
    enu_verts = [v2t_conv(point) for point in vertical_verts]
    if verbose:
        plog(f'{enu_verts = }')


    # Create a layer of points with the vertices of the image
    lat, lon = metadata.get_latlon(tags, maker, model)
    crs = f'PROJ:+proj=nsper +h={alt} +lat_0={lat} +lon_0={lon} +datum=WGS84 +type=crs'
    vlayers.create_layer_from_points(enu_verts, crs)


    # Get the approximate bounding box of the image rectified in topocentric coordinates
    approx_bbox = boundingbox.get_bbox(enu_verts)
    if verbose:
        plog(f'{approx_bbox = }')
    xmin, ymin, xmax, ymax = approx_bbox
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2

    # Compute GSD if needed
    if gsd == 0.0:
        # Get the pixel size as GSD if image were vertical.
        gsd = pixel_size * alt / focal_length

    # Compute row and columns for georeferenced image
    georef_cols = int(np.ceil((xmax - xmin) / gsd))
    georef_rows = int(np.ceil((ymax - ymin) / gsd))

    if verbose:
        plog(f'{gsd = }')
        plog(f'{georef_rows = }')
        plog(f'{georef_cols = }')

    # Redefine bounding box from new center, gsd, rows and columns information
    xmin = x_center - gsd * (georef_cols / 2)
    xmax = x_center + gsd * (georef_cols / 2)
    ymin = y_center - gsd * (georef_rows / 2)
    ymax = y_center + gsd * (georef_rows / 2)

    bbox = [xmin, ymin, xmax, ymax]
    if verbose:
        plog(f'{bbox = }')

    # Define the geotransform matrix
    geotrans = [xmin, 0, gsd, ymax, 0 -gsd]

    # Convert from topocentric (enu) to georeferenced image (col, row) coordinates
    t2i_conv = transformations.t2i_converter(xmin, ymax, gsd)
    # Discard Up coordinate of topocentric points
    georef_image_verts = np.array([t2i_conv(point[0:2]) for point in enu_verts])
    if verbose:
        plog(f'{georef_image_verts = }')

    # Transform source to rectified array using homography
    if with_opencv:
        try:
            from mochila.raster.single_view import image_with_opencv
            georef_image = image_with_opencv.create(orig_image_bounds,
                                                georef_image_verts,
                                                georef_rows,
                                                georef_cols,
                                                utf8_path,
                                                verbose=verbose)
        except ImportError as e:
            plog("'with_opencv' argument is True but OpenCV can't be imported.",
                "Install OpenCV or call this function with 'with_opencv=False' keyword argument.")
            raise e
    else:
        from mochila.raster.single_view import image_without_opencsv
        georef_image = image_without_opencv.create(orig_image_bounds,
                                                georef_image_verts,
                                                georef_rows,
                                                georef_cols,
                                                utf8_path,
                                                verbose=verbose)



