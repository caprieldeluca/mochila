# -*- coding: utf-8 -*-

import numpy as np


def create_matrix(axis, angle):
    """Create the rotation matrix around an axis.

    Rotation matrices follows the Tait–Bryan convention for a chained rotation:
    https://en.wikipedia.org/wiki/Davenport_chained_rotations#Tait%E2%80%93Bryan_chained_rotationsx is for system.
    -----
    Params:
        axis:       str
            The axis around the rotation is computed.
            Accepted values are 'x', 'y' or 'z'.
            The system is considered right-hand, with 'x' being the 'roll' (longitudinal) axis,
             'y' being the 'pitch' (transversal) axis, and 'z' being the 'yaw' (normal) axis.
        angle:      float
            The rotation angle, in radians.
    -----
    Returns:
        R:      ndarray
            Rotation matrix.
    """

    R = np.zeros(shape=(3, 3))

    cos, sin = np.cos(angle), np.sin(angle)

    if axis == 'x':
        #      | 1     0        0    |
        # Rx = | 0   cos(r)  -sin(r) |
        #      | 0   sin(r)   cos(r) |

        R[0, 0] = 1
        R[1, 1] = cos
        R[1, 2] = -sin
        R[2, 1] = sin
        R[2, 2] = cos

    elif axis == 'y':
        #      |  cos(p)  0   sin(p) |
        # Ry = |    0     1     0    |
        #      | -sin(p)  0   cos(p) |

        R[0, 0] = cos
        R[0, 2] = sin
        R[1, 1] = 1
        R[2, 0] = -sin
        R[2, 2] = cos

    elif axis == 'z':
        #      |  cos(y)  -sin(y)  0 |
        # Rz = |  sin(y)   cos(y)  0 |
        #      |    0        0     1 |

        R[0, 0] = cos
        R[0, 1] = -sin
        R[1, 0] = sin
        R[1, 1] = cos
        R[2, 2] = 1

    else:
        raise Exception(f"Axis parameter '{axis}' is not 'x', 'y' nor 'z'.")

    return R
