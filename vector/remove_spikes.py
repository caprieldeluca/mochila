# -*- coding: utf-8 -*-
from mochila import plog

import math

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsProcessing,
    QgsProject,
    QgsVectorLayer)

import numpy as np
from mochila.mnumpy import nputils


def run(geom, threshold):
    """Delete vertices if angle is less than threshold degrees."""

    verts = geom.vertices()

    for i, v in enumerate(verts):
        iprev, inext = geom.adjacentVertices(i)
        prev_point = geom.vertexAt(iprev)
        curr_point = geom.vertexAt(i)
        next_point = geom.vertexAt(inext)

        angle = nputils.get_angle_at_point(
                                        prev_point,
                                        curr_point,
                                        next_point)

        angle_degrees = math.degrees(angle)

        if angle_degrees <= threshold:
            geom.deleteVertex(i)
            plog(f"Deleted vertex at ({curr_point.x()}, {curr_point.y()}) with angle: {angle_degrees:.2f} degrees.")


    return geom



def test():

    wkt = "Multipolygon("
    wkt += "((0 0, 10 0, 10 10, 9.9 5, 0 10, 0 0),(1 1, 2 1, 2 2, 1 2, 1.5 1.9, 1 1)),"
    wkt += "((15 0, 20 0, 16 0.1, 20 0.2, 20 1, 19.9 0.3, 19 1, 20 5, 15 5, 15 0))"
    wkt += ")"
    geometry = QgsGeometry.fromWkt(wkt)

    layer = QgsVectorLayer(
        path='Polygon',
        baseName='With spikes',
        providerLib='memory')

    feature = QgsFeature(
        id=0)

    feature.setGeometry(
        geometry)

    flist = [feature]

    layer.dataProvider().addFeatures(
        flist)

    QgsProject.instance().addMapLayer(
        layer)

    #####
    # Remove spikes and add the new geometry to a new layer
    #####

    poly_without_spikes = run(geometry, 15)


    layer = QgsVectorLayer(
        path='Polygon',
        baseName='Without spikes',
        providerLib='memory')

    feature = QgsFeature(
        id=0)

    feature.setGeometry(
        poly_without_spikes)

    flist = [feature]

    layer.dataProvider().addFeatures(
        flist)

    QgsProject.instance().addMapLayer(
        layer)



