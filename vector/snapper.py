# -*- coding: utf-8 -*-
from mochila import plog


from qgis.analysis import (
    QgsGeometrySnapper
)
from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsVectorLayer
)


snapper_modes = {
      'PreferNodes': 0,
      'PreferClosest': 1,
      'PreferNodesNoExtraVertices': 2,
      'PreferClosestNoExtraVertices': 3,
      'EndPointPreferNodes': 4,
      'EndPointPreferClosest': 5,
      'EndPointToEndPoint': 6
}

def create_scratch_reference_layer():
    """Create a scratch reference layer to snap to"""
    # url for a scratch memory layer
    url = 'Polygon'

    r1 = QgsVectorLayer(
        path=url,
        baseName='x',
        providerLib='memory'
    )

    refGeom = QgsGeometry.fromWkt(
        wkt="Polygon((0 0, 10 0, 10 10, 0 10, 0 0))"
    )

    ff = QgsFeature(
        id=0
    )

    ff.setGeometry(
        geometry=refGeom
    )

    # flist is a QgsFeatureList type object in C++ API
    flist = [ff]

    r1.dataProvider().addFeatures(
        flist=flist
    )

    return r1


def test_geometry_snapper():
    """Test snap a geometry to a reference layer"""

    polygonGeom = QgsGeometry.fromWkt(
        wkt="Polygon((0.1 -0.1, 10.1 0, 9.9 10.1, 0 10, 0.1 -0.1))"
    )

    # Create reference layer and assign to Python variable before use
    #  (https://lists.osgeo.org/pipermail/qgis-developer/2023-October/066176.html)
    referenceSource = create_scratch_reference_layer()

    # Create the snapper object
    snapper = QgsGeometrySnapper(
        referenceSource
    )

    # snapGeometry: Snaps a geometry to the reference layer and returns the result
    result = snapper.snapGeometry(
        geometry=polygonGeom,
        snapTolerance=1,

    )

    plog("result =", result)

    return result

