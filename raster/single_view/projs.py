# -*- coding: utf-8 -*-

from mochila import plog

from pyproj import Transformer
import numpy as np

def enu2wgs(enu, lat, lon, h):
    """Transform ENU to WGS84 coordinates."""

    pipeline_str = f"""
    +proj=pipeline
    +step +inv +proj=topocentric +lon_0={lon} +lat_0={lat} +h_0={20}
    +step +inv +proj=cart +ellps=WGS84
    """
    pipeline_str = ' '.join(pipeline_str.split())

    pipe_trans = Transformer.from_pipeline(pipeline_str)

    # Pyproj transformers expect list of coordinates instead of points, so transpose
    e, n, u = np.array(enu).T

    wgs = pipe_trans.transform(e, n, u)

    # Return list of points instead of coordinates, so transpose
    return np.array(wgs).T

