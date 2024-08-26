# -*- coding: utf-8 -*-
from mochila import plog

import os


from osgeo import ogr
from qgis.analysis import QgsGeometrySnapper

from qgis.core import (
    QgsFeatureSource,
    QgsProject,
    QgsVectorLayer)


def get_layer_from_gpkg(utf8_path, baseName):
    """Get a QgsVectorLayer from a GeoPackage file path and layer name"""
    layer = None

    datasource = ogr.Open(
        utf8_path)

    layer_names = [l.GetName() for l in datasource]

    # QGIS ogr provider path to the layer
    path = utf8_path + "|layername=" + baseName
    provider = 'ogr'

    if baseName in layer_names:
        layer = QgsVectorLayer(
            path,
            baseName,
            provider)
    else:
        plog(f'Error: there is no layer named "{baseName}" in {utf8_path}')

    datasource = None

    return layer

def load_layer_to_map(mapLayer):
    """Load a layer to the map"""

    QgsProject.instance().addMapLayer(
        mapLayer)

    return mapLayer
