# -*- coding: utf-8 -*-
from mochila import plog

import numpy as np


# https://stackoverflow.com/a/13849249
def get_angle_at_point(
                    prev_point,
                    curr_point,
                    next_point):
    """Compute the angle at current point given previous and next ones."""

    # Create two vectors from current to previous and next points
    v1 = np.array([
            prev_point.x() - curr_point.x(),
            prev_point.y() - curr_point.y()])

    v2 = np.array([
            next_point.x() - curr_point.x(),
            next_point.y() - curr_point.y()])

    # Create unit vectors
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)

    # Compute the angle
    angle = np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

    return angle

def get_band_statistics(band_arr, nodata):
    """Compute the median and percentiles 5 and 95 of a band array."""

    # Mask and compress (flat and delete all nodata values) the band
    flat_values = np.ma.masked_equal(band_arr, nodata).compressed()
    # mean
    mean = np.mean(flat_values)
    # median
    median = np.median(flat_values)
    # Standard deviation
    std = np.std(flat_values)
    # Percentile 5
    p5 = np.percentile(flat_values, 5)
    # Percentile 95
    p95 = np.percentile(flat_values, 95)

    return mean, median, std, p5, p95
