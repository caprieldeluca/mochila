# -*- coding: utf-8 -*-
from mochila import plog

import os


from osgeo import ogr
from qgis.analysis import QgsGeometrySnapper

from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsFeatureSource,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer)
from qgis.utils import iface


#=====
# GET CURRENT LAYER
#=====
def get_current_layer():
    """Get the current layer of the project."""

    layer = iface.layerTreeView().currentLayer()

    return layer

#=====
# GET LAYER BY NAME
#=====
def get_layer_by_name(name):
    """Get a layer of the project by its name."""
    layer = QgsProject.instance().mapLayersByName(name)[0]

    return layer

#=====
# GET LAYER FROM GPKG
#=====
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


#=====
# LOAD LAYER TO MAP
#=====
def load_layer_to_map(mapLayer):
    """Load a layer to the map"""

    QgsProject.instance().addMapLayer(
        mapLayer)

    return mapLayer


#=====
# GET FEATURES COUNT
#=====
def get_features_count(layer):
    """Get the features count of a layer"""

    feats = layer.getFeatures(QgsFeatureRequest())
    count = len(list(feats))

    return count


#=====
# GET REF GEOM
#=====
def get_ref_geom(layer):
    """Get multipart geometry as union of all geometries from a layer."""

    feats = layer.getFeatures(QgsFeatureRequest())
    for i, f in enumerate(feats):
        if i == 0:
            g = f.geometry()
        else:
            g = f.geometry().combine(g)

    return g


#=====
# CREATE POINTS LAYER FROM POINTS COORDINATES AND CRS
#=====
def create_layer_from_points(points, crs):
    """Create new memory layer with points and crs."""

    layer = QgsVectorLayer(
        path=f'Point?crs={crs}&field=id:integer',
        baseName='points',
        providerLib='memory')

    for idx, point in enumerate(points):
        feature = QgsFeature(layer.fields(), idx)
        qgspoint = QgsPointXY(point[0], point[1])
        geometry = QgsGeometry.fromPointXY(qgspoint)
        feature.setAttribute(0, idx)
        feature.setGeometry(geometry)
        flist = [feature]

        layer.dataProvider().addFeatures(flist)

    QgsProject.instance().addMapLayer(
        layer)
