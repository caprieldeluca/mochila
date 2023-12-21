# -*- coding: utf-8 -*-
from mochila import plog, pkg_path
from mochila.vector import vlayers

import os

from qgis import processing
from qgis.analysis import (
    QgsGeometrySnapper)
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsProcessing,
    QgsProject,
    QgsVectorLayer)


def test_cluster():
    """Test k-means clustering."""

    utf8_path = os.path.join(pkg_path,'vector','data','points.gpkg')

    baseName = 'points'

    layer = vlayers.get_layer_from_gpkg(utf8_path, baseName)

    # Number of clusters
    k = 5

    params = {
        'INPUT': layer,
        'CLUSTERS': k,
        'FIELD_NAME': 'CLUSTER_ID',
        'SIZE_FIELD_NAME': 'CLUSTER_SIZE',
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}

    result = processing.run("native:kmeansclustering", params)

    return result
