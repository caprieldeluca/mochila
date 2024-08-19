# -*- coding: utf-8 -*-

from qgis.core import (
    QgsRasterFileWriter,
    QgsRasterLayer,
)
from mochila import plog



#=====
# GET LAYER FROM GeoTIFF
#=====
def get_layer_from_geotiff(uri, baseName):
    """Get a QgsRasterLayer from a GeoTiff file path and layer name"""

    layer = QgsRasterLayer(uri, baseName)

    return layer


#####
# Get Raster File Writer by extension
#####
def get_raster_file_writer(extension):
    """Get the raster file writer object from extension.

    Example: plog(get_raster_file_writer('tif')).
    """
    return QgsRasterFileWriter.driverForExtension(extension)

