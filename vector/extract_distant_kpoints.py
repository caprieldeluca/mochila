# -*- coding: utf-8 -*-
from mochila import plog, pkg_path
from mochila.vector import (
    vlayers,
    cluster)

import os

from qgis import processing
from qgis.core import (
    QgsGeometry,
    QgsFeature,
    QgsProcessing,
    QgsVectorLayer)


#####
# DEFAULT RUN
#####

def run(layer, k):
    """Extract spatial distributed k points from a points layer."""

    results = {}


    #####
    # K-MEANS CLUSTERING
    #####
    params = {
    'INPUT': layer,
    'CLUSTERS': k,
    'FIELD_NAME': 'CLUSTER_ID',
    'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}

    results['cluster'] = processing.run("native:kmeansclustering", params)


    #####
    # DISSOLVE
    #####
    params = {
        'INPUT': results['cluster']['OUTPUT'],
        'FIELD': 'CLUSTER_ID',
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}

    results['dissolve'] = processing.run('native:dissolve', params)


    #####
    # CENTROIDS
    #####
    params = {
        'INPUT': results['dissolve']['OUTPUT'],
        'ALL_PARTS': False,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}

    results['centroids'] = processing.run('native:centroids', params)


    #####
    # SQL
    #####

    fields = results['cluster']['OUTPUT'].fields()

    # Definir la consulta
    query = 'WITH distancias AS (SELECT '
    for name in fields.names():
        query += 't."' + name + '" , '
    query += 'Distance(t.geometry, c.geometry) AS dist, '
    query += 't.geometry AS geometry '
    query += 'FROM input1 AS t JOIN input2 AS c '
    query += 'ON t.CLUSTER_ID = c.CLUSTER_ID '
    query += '), muestras AS (SELECT '
    for name in fields.names():
        query += '"' + name + '" , '
    query += 'Min(d.dist) AS dist, '
    query += 'geometry AS geometry '
    query += 'FROM distancias AS d GROUP BY CLUSTER_ID'
    query += ') SELECT '
    for name in fields.names():
        query += '"' + name + '" , '
    query += 'geometry AS geometry '
    query += 'FROM muestras;'

    # Execute SQL
    params = {
        'INPUT_DATASOURCES': [results['cluster']['OUTPUT'], results['centroids']['OUTPUT']],
        'INPUT_GEOMETRY_CRS': '',
        'INPUT_GEOMETRY_FIELD': '',
        'INPUT_GEOMETRY_TYPE': 2, #Point
        'INPUT_QUERY': query,
        'INPUT_UID_FIELD': '',
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}

    results['sql'] = processing.run('qgis:executesql', params)

    result_layer = results['sql']['OUTPUT']

    vlayers.load_layer_to_map(
        mapLayer=result_layer)

    plog("resluts =", results)


#####
# SIMPLE TEST WITH A GEOPACKAGE LAYER
#####

def test():
    """Test the run function with a layer and k values"""

    utf8_path = os.path.join(pkg_path,'vector','data','points.gpkg')

    baseName = 'points'

    layer = vlayers.get_layer_from_gpkg(utf8_path, baseName)

    k = 5

    run(layer, k)


#####
# TEST WHEN K VALUE GREATER THAN N FEATURES
#####

def test_k_gt_n():
    """Test if k value is greater than n features in layer"""

    layer = QgsVectorLayer(
        path='Point',
        baseName='point',
        providerLib='memory')

    flist = []

    for n in range(4):
        geometry = QgsGeometry.fromWkt(
            wkt=f"Point({n} 0)")

        feature = QgsFeature(
            id=n)

        feature.setGeometry(
            geometry)

        flist.append(feature)

    layer.dataProvider().addFeatures(
        flist)

    k = 5

    run(layer, k)

