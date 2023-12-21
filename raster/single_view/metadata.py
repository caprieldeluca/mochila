# -*- coding: utf-8 -*-

from mochila import plog

import numpy as np

from qgis.core import (
    QgsExifTools
)

PRINTS = True


def get_tags(imagePath):
    """Get tags from image file."""

    tags = QgsExifTools.readTags(imagePath)
    if not tags:
        raise Exception(f"Can't read EXIF tags from {imagePath}.")

    return tags


def get_mm(tags):
    """Get Maker and Model from metadata tags."""

    maker = tags["Exif.Image.Make"]
    model = tags["Exif.Image.Model"]

    return maker, model


def get_rowscols(tags, maker, model):
    """Get rows and cols of image from metadata tags."""

    rows = tags['Exif.Photo.PixelYDimension']
    cols = tags['Exif.Photo.PixelXDimension']

    return rows, cols


def get_rpy(tags, maker, model):
    """Get Roll, Pitch and Yaw angles from metadata."""

    if maker == "DJI":
        if model == "FC7303": # DJI Mini 2
            r = float(tags['Xmp.drone-dji.FlightRollDegree'])
            p = float(tags['Xmp.drone-dji.FlightPitchDegree'])
            y = float(tags['Xmp.drone-dji.FlightYawDegree'])

    return r, p, y


def get_altitude(tags, maker, model):
    """Get camera altitude relative to ground."""

    if maker == "DJI":
        h = float(tags['Xmp.drone-dji.RelativeAltitude'])

    return h


def get_latlon(tags, maker, model):
    """Process tags of image and return relevant data."""

    longitude = tags["Exif.GPSInfo.GPSLongitude"]
    lon_ref = tags['Exif.GPSInfo.GPSLongitudeRef']
    if lon_ref == "W":
        longitude = -longitude

    latitude = tags["Exif.GPSInfo.GPSLatitude"]
    lat_ref = tags['Exif.GPSInfo.GPSLatitudeRef']
    if lat_ref == "S":
        latitude = -latitude

    return latitude, longitude



