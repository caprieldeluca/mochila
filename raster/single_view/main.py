# -*- coding: utf-8 -*-

from mochila import plog
from mochila.vector import vlayers
from mochila.raster.single_view import (
    boundingbox,
    image,
    metadata,
    projs,
    transformations
)
from mochila.utils import gdal_utils

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



def process(src_utf8_path,
            dst_utf8_path,
            dst_crs=None, *,
            corrections=CORRECTIONS,
            gsd=0.0,
            sensor_widths=SENSOR_WIDTHS,
            verbose=True):
    """Process the georeference of a single-view perspective image.
    -----
    Parameters:
        src_uft8_path:  str
                Path to source image file.
        dst_uft8_path:  str
                Path to destination image file.
        dst_crs:        str (optional)
                Destination Spatial Reference System to project to the source dataset.
                Any string accepted by OGRSpatialReference.SetFromUserInput().
                If None, WGS84 / UTM zone will be computed from the image EXIF Geotags.
                Dafaults to None.
        corrections:    dict (optional, keyword only)
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
        verbose:        bool (optional, keyword only)
                Control if print some information or not.
                Defaults to True.
    Return:
        georef_path:    str
                Path to georeferenced image file.
    """

    corrections = _verify_corrections(corrections)

    tags = metadata.get_tags(src_utf8_path)

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
    # Define topocentric CRS in QgsCoordinateReferenceSystem().createFromString() format
    topo_crs = f'PROJ:+proj=tmerc +lat_0={lat} +lon_0={lon} +datum=WGS84 +type=crs'
    if verbose:
        plog(f'{topo_crs = }')
    #vlayers.create_layer_from_points(enu_verts, topo_crs)


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
    geotrans = [xmin, gsd, 0, ymax, 0, -gsd]
    if verbose:
        plog(f'{geotrans = }')

    # Convert from topocentric (enu) to georeferenced image (col, row) coordinates
    t2i_conv = transformations.t2i_converter(xmin, ymax, gsd)
    # Discard Up coordinate of topocentric points
    georef_image_verts = np.array([t2i_conv(point[0:2]) for point in enu_verts])
    if verbose:
        plog(f'{georef_image_verts = }')

    # Transform source to rectified array using homography
    georef_image_array = image.rectify(orig_image_bounds,
                                georef_image_verts,
                                georef_rows,
                                georef_cols,
                                src_utf8_path,
                                verbose=verbose)

    # The georef_image_array comes with shape (rows, columns, bands)
    # We need it as (bands, rows, columns) to write the dataset
    bands_first = np.moveaxis(georef_image_array, -1, 0)

    # For some reason (TODO: investigate) the bands comes as brga
    # bands_first: [blue, red, green, alpha]
    # Convert to rgba:
    rgba_array = np.array([bands_first[2], bands_first[1], bands_first[0], bands_first[3]])

    if verbose:
        plog(f'{rgba_array.shape = }')

    # Get a GeoTIFF driver dataset stored in memory with the rectified image
    topocentric_ds = gdal_utils.array2ds(rgba_array,
                                        geotrans,
                                        topo_crs[5:], # PROJ: prefix is not used by osr
                                        verbose=verbose)


    if not dst_crs:
        # Get EPSG id of WGS84 / UTM Zone from EXIF Geotags
        zone = int(np.floor(lon / 6) + 31)
        hemisf = 326 if lat >= 0 else 327
        dst_crs = "EPSG:" + str(hemisf) + str(zone)
    if verbose:
        plog(f'{dst_crs = }')

    # Reproject rectified image and save to disk
    warped_ds = gdal_utils.warp_ds(dst_utf8_path,
                                topocentric_ds,
                                dst_crs,
                                verbose=verbose)

    # Close datasets
    warped_ds = None
    topocentric_ds = None

