# -*- coding: utf-8 -*-
from mochila import plog

def get_geometry_type(geometryName):

    # Definir el geometryType dependiendo la versión de QGIS:
    if Qgis.QGIS_VERSION_INT < 33000:
        geometryType = QgsWkbTypes.Point
    else:
        geometryType = Qgis.WkbType.Point
