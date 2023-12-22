# -*- coding: utf-8 -*-

from mochila import plog
from mochila.raster.single_view import rotation
import numpy as np


def i2o_converter(rows, cols, pixel_size, focal_length):
    """Create a converter from image to oblique camera coordinates with given parameters."""

    def converter(rowcol):
        """Transform from image (row, col) to oblique camera ("front, right, down") coordinates."""
        row, col = rowcol

        f = (- row + 0.5 * rows) * pixel_size
        r = (col - 0.5 * cols) * pixel_size
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

        enu = np.array([h*y/z, h*x/z, 0])

        return enu

    return converter


def t2i_converter(xmin, ymax, gsd):
    """Create a converter from topocentric to georeferenced image with given parameters."""

    def converter(point):
        """Transform a point (x, y) from topocentric to image (row, col) coordinates."""
        x, y = point

        row = (ymax - y) / gsd
        column = (x - xmin) / gsd

        rowcol = np.array([row, column])

        return rowcol

    return converter
