# -*- coding: utf-8 -*-

from mochila import plog
from mochila.raster.single_view import rotation
import numpy as np


def i2o_converter(rows, cols, pixel_size, focal_length):
    """Create a converter from image to oblique camera coordinates with given parameters.
    -----
    Params:
        rows:           int
            Rows count of image.
        cols:           int
            Columns count of image
        pixel_size:     float
            Size of the pixel at sensor, in meters.
        focal_lenght:   float
            Focal lenght of sensor, in meters.
    Returns:
        converter:      callable
            Function to convert from image to oblique camera coordinates
    """

    def converter(colrow):
        """Transform from image (col, row) to oblique camera ("front, right, down") coordinates.
        -----
        Params:
            colrow:         list
                List of column (float) and row (float) coordinates in image system
                 to be converted to oblique camera coordinates.
        -----
        Returns:
            frd             ndarray
                Array with Front, Right and Down coordinates in the oblique
                 camera system.
        """
        col, row = colrow

        # Unsimplified equations for better understanding
        f = (- row + (rows/2 - 0.5)) * pixel_size
        r = (col - (cols/2 - 0.5)) * pixel_size
        d = focal_length

        frd = np.array([f, r, d])

        return frd

    return converter


def o2v_converter(rpy):
    """Create a converter from oblique to vertical camera coordinates with given parameters.

    Parameter are Roll, Pitch and Yaw, which are the angles arond right-hand
     Cartesian system of Front, Right and Down axis.
    """

    r, p, y = np.radians(rpy)

    Rx = rotation.create_matrix('x', r)
    Ry = rotation.create_matrix('y', p)
    Rz = rotation.create_matrix('z', y)
    R = Rz @ Ry @ Rx

    def converter(frd):
        """Transform Front, Right and Down coordinates from oblique camera
            to xyz coordinates of vertical system."""

        xyz = np.dot(R, frd)

        return xyz

    return converter



def v2t_converter(alt):
    """Create a converter from vertical camera to topocentric coordinates with given parameters."""
    h = alt

    def converter(xyz):
        """Project points from vertical camera (xyz) coordinates to topocentric (ENU) plane (U=0).

        The camera center coordinates are E=0, N=0, U=h."""

        x, y, z = xyz

        # Up = 0 coordinate is preserved in case it is needed later
        enu = np.array([h*y/z, h*x/z, 0])

        return enu

    return converter


def t2i_converter(xmin, ymax, gsd):
    """Create a converter from topocentric to georeferenced image with given parameters.
    -----
    Params:
        xmin:           float
            Coordinate of the West side, in meters.
        ymax:           float
            Coordinate of the North side, in meters.
        gsd:            float
            Size of the pixel of georeferenced image, in meters.
    -----
    Returns:
        converter       callable
            Function to convert from topocentric to georeferenced image
             a pair of point coordinates.
    """

    def converter(point):
        """Transform a point (x, y) from topocentric to image (col, row) coordinates.
        -----
        Params:
            point        list
                List of East (float) and North (float) coordinates of a point.
        -----
        Returns:
            colrow          ndarray
                Array of column (float) and row (float) coordinates in
                 the georeferenced image system.
        """
        x, y = point


        col = ((x - xmin) / gsd) - 0.5
        row = ((ymax - y) / gsd) - 0.5

        colrow = np.array([col, row])

        return colrow

    return converter
