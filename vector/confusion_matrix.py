# -*- coding: utf-8 -*-

from pathlib import PurePath

from qgis import processing
from qgis.core import (
    QgsGeometry,
    QgsFeatureRequest,
    QgsProcessing,
    QgsProcessingContext)

from mochila import plog
from mochila.vector import layers


#=====
# RUN
#=====
def run(samples, results, attr_name):
    """Compute the confusion matrix from samples and results."""

    # Verify that samples layer only have two values in "attr_name"
    idx = samples.fields().indexOf(attr_name)
    values = list(samples.uniqueValues(idx))

    if len(values) != 2:
        msg = f'The attribute "{attr_name}" must have two values, but '
        msg += f'{values} values were found.'
        plog(msg)
        return


    # Reference geometry to analyze intersections
    ref_geom = layers.get_ref_geom(results)

    # Count all features
    samples_count = layers.get_features_count(samples)
    plog("Cantidad total de muestras =", samples_count)


    #=====
    # Create layers for first and second values
    #  and evaluate the intersection with reference geom
    #=====

    # LYR1
    lyr1 = request_by_attribute(samples, attr_name, values[0])
    lyr1_count = layers.get_features_count(lyr1)

    lyr1a = request_by_intersection(lyr1, ref_geom)
    lyr1a_count = layers.get_features_count(lyr1a)
    lyr1b_count = lyr1_count - lyr1a_count

    msg = f'Cantidad total de muestras con "{attr_name}" = {values[0]}: '
    msg += '***' + str(lyr1_count) + '***\n'
    msg += 'De los cuales: \n'
    msg += f'***{lyr1a_count}*** intersecan con la capa de resultados.\n'
    msg += f'***{lyr1b_count}*** NO intersecan con la capa de resultados.'
    plog(msg)

    # LYR1
    lyr2 = request_by_attribute(samples, attr_name, values[1])
    lyr2_count = layers.get_features_count(lyr2)

    lyr2a = request_by_intersection(lyr2, ref_geom)
    lyr2a_count = layers.get_features_count(lyr2a)
    lyr2b_count = lyr2_count - lyr2a_count

    msg = f'Cantidad total de muestras con "{attr_name}" = {values[1]}: '
    msg += '***' + str(lyr2_count) + '***\n'
    msg += 'De los cuales: \n'
    msg += f'***{lyr2a_count}*** intersecan con la capa de resultados.\n'
    msg += f'***{lyr2b_count}*** NO intersecan con la capa de resultados.'
    plog(msg)


#=====
# REQUEST BY ATTRIBUTE
#=====
def request_by_attribute(layer, attr_name, attr_value):
    """Request the features with attr_value and geom intersection."""
    req = QgsFeatureRequest()
    req.setFilterExpression(f'"{attr_name}" = \'{attr_value}\'')
    #req.setDistanceWithin(geometry=geom, distance=0)

    requested_layer = layer.materialize(req)

    return requested_layer


#=====
# REQUEST BY INTERSECTION
#=====
def request_by_intersection(layer, geom):
    """Request the features with attr_value and geom intersection."""
    req = QgsFeatureRequest()
    req.setDistanceWithin(geometry=geom, distance=0)

    requested_layer = layer.materialize(req)

    return requested_layer


#=====
# TEST
#=====
def test():
    """Test the confusion matrix from two geopackage layers."""

    # Get results layer
    utf8_path = str(PurePath(__file__).parent / 'data' / 'classification' / 'results.gpkg')
    baseName = 'results'
    results = layers.get_layer_from_gpkg(utf8_path, baseName)

    # Get samples layer
    utf8_path = str(PurePath(__file__).parent / 'data' / 'classification' / 'samples.gpkg')
    baseName = 'samples'
    samples = layers.get_layer_from_gpkg(utf8_path, baseName)

    # Attribute name with classification
    attr_name = 'class'

    run(samples, results, attr_name)

