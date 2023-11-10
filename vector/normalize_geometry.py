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

    vertslist = [v for v in geom.vertices()]

    for n in range(len(vertslist)-1):
        nprev, nnext = geom.adjacentVertices(n)
        prev_point = geom.vertexAt(nprev)
        curr_point = geom.vertexAt(n)
        next_point = geom.vertexAt(nnext)

        was_found, vertex_id = geom.vertexIdFromVertexNr(n)

        angle = nputils.get_angle_at_point(
                                        prev_point,
                                        curr_point,
                                        next_point)

        angle_degrees = math.degrees(angle)

        if angle_degrees <= threshold:
            geom.deleteVertex(n)
            plog(f"Deleted vertex at ({curr_point.x()}, {curr_point.y()}) with angle: {angle_degrees:.2f} degrees.")



    layer = QgsVectorLayer(
        path='Polygon',
        baseName='y',
        providerLib='memory')

    feature = QgsFeature(
        id=0)

    feature.setGeometry(
        geom)

    flist = [feature]

    layer.dataProvider().addFeatures(
        flist)

    QgsProject.instance().addMapLayer(
        layer)


    return geom


def test():

    wkt = "Multipolygon("
    wkt += "((0 0, 10 0, 10 10, 9.9 5, 0 10, 0 0),(1 1, 2 1, 2 2, 1 2, 1.5 1.9, 1 1)),"
    wkt += "((15 0, 20 0, 16 0.1, 20 0.2, 20 1, 19.9 0.3, 19 1, 20 5, 15 5, 15 0))"
    wkt += ")"
    geometry = QgsGeometry.fromWkt(wkt)

    layer = QgsVectorLayer(
        path='Polygon',
        baseName='x',
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

    normalized_poly = run(geometry, 15)




