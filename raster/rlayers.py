# -*- coding: utf-8 -*-

from qgis.core import QgsRasterLayer
from mochila import plog



#=====
# GET LAYER FROM GeoTIFF
#=====
def get_layer_from_geotiff(uri, baseName):
    """Get a QgsRasterLayer from a GeoTiff file path and layer name"""

    layer = QgsRasterLayer(uri, baseName)

    return layer

