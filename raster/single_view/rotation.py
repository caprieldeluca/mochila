# -*- coding: utf-8 -*-

import numpy as np


def create(axis, angle):
    """Create the rotation matrix around an axis.
    -----
    Params:
        axis:   'x', 'y' or 'z'. The axis around the rotation is computed.
                    the system is considered right-handle.

        angle:  The angle in radians.
    -----
    Returns:
        R:      Rotation matrix (numpy array).

    """

    R = np.zeros(shape=(3, 3))

    cos, sin = np.cos(angle), np.sin(angle)

    if axis == 'x':
        #      | 1       0        0  |
        # Rx = | 0    cos(r)  sin(r) |
        #      | 0   -sin(r)  cos(r) |

        R[0, 0] = 1
        R[1, 1] = cos
        R[1, 2] = sin
        R[2, 1] = -sin
        R[2, 2] = cos

    elif axis == 'y':
        #      | cos(p)   0  -sin(p) |
        # Ry = |    0     1     0    |
        #      | sin(p)   0   cos(p) |

        R[0, 0] = cos
        R[0, 2] = -sin
        R[1, 1] = 1
        R[2, 0] = sin
        R[2, 2] = cos

    elif axis == 'z':
        #      | cos(y)   sin(y)   0 |
        # Rz = | -sin(y)  cos(y)   0 |
        #      |    0        0     1 |

        R[0, 0] = cos
        R[0, 1] = sin
        R[1, 0] = -sin
        R[1, 1] = cos
        R[2, 2] = 1

    else:
        raise Exception(f"Axis parameter '{axis}' is not 'x', 'y' nor 'z'.")

    return R
