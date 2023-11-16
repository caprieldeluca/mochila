# -*- coding: utf-8 -*-

from pathlib import PurePath

import numpy as np
from qgis import processing
from qgis.core import (
    QgsCoordinateTransformContext,
    QgsGeometry,
    QgsFeatureRequest,
    QgsProcessing,
    QgsProcessingContext,
    QgsProject)


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
    context = QgsProcessingContext()
    params = {
        'INPUT': results,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }
    dissolve_dict = processing.run(
        'native:dissolve',
        params,
        context=context,
        is_child_algorithm=True)

    dissolved = context.getMapLayer(dissolve_dict['OUTPUT'])
    ref_feats = dissolved.getFeatures(QgsFeatureRequest())
    ref_geom = next(ref_feats).geometry()
    ref_crs = dissolved.crs()

    # Count all features
    samples_count = layers.get_features_count(samples)
    plog("Cantidad total de muestras =", samples_count)


    #=====
    # Create layers for first (1) and second (2) predicted values,
    #  evaluate the intersection (a) or not (b) with reference geom
    #  and count features
    #=====


    # LYR1
    lyr1 = request_by_attribute(samples, attr_name, values[0])
    lyr1_count = layers.get_features_count(lyr1)

    lyr1a = request_by_intersection(lyr1, ref_geom, ref_crs)
    lyr1a_count = layers.get_features_count(lyr1a)
    lyr1b_count = lyr1_count - lyr1a_count

    msg = f'Cantidad total de muestras con "{attr_name}" = {values[0]}: '
    msg += '**' + str(lyr1_count) + '**\n'
    msg += 'De los cuales: \n'
    msg += f'**{lyr1a_count}** intersecan con la capa de resultados.\n'
    msg += f'**{lyr1b_count}** NO intersecan con la capa de resultados.'
    plog(msg)

    # LYR1
    lyr2 = request_by_attribute(samples, attr_name, values[1])
    lyr2_count = layers.get_features_count(lyr2)

    lyr2a = request_by_intersection(lyr2, ref_geom, ref_crs)
    lyr2a_count = layers.get_features_count(lyr2a)
    lyr2b_count = lyr2_count - lyr2a_count

    msg = f'Cantidad total de muestras con "{attr_name}" = {values[1]}: '
    msg += '**' + str(lyr2_count) + '**\n'
    msg += 'De los cuales: \n'
    msg += f'**{lyr2a_count}** intersecan con la capa de resultados.\n'
    msg += f'**{lyr2b_count}** NO intersecan con la capa de resultados.'
    plog(msg)


    #=====
    # Create predicted columns, decide their means by the sum
    #  of the diagonal and create the confusion matrix.
    #=====

    # Predicted columns for values (1) and (2)
    pred_1 = [lyr1a_count, lyr1b_count]
    pred_2 = [lyr2a_count, lyr2b_count]

    # Create confusion matrix from best accuracy between
    # (1) means intersection (a) or not
    msg = "Se considera que los resultados representan al valor "
    if lyr1a_count + lyr2b_count >= lyr1b_count + lyr2a_count:
        v1_means_a = True
        msg += f'{values[0]} en el atributo "{attr_name}".'
        cm = np.array([pred_1, pred_2])

    else:
        v1_means_a = False
        msg += f'{values[1]} en el atributo "{attr_name}".'
        cm = np.array([pred_2, pred_1])
    plog(msg)
    plog("Confusion matrix:\n", cm.T)


    #=====
    # Compute accuracy and Cohen's kappa coefficient.
    #=====

    acc = np.trace(cm) / np.sum(cm)
    plog("Accuracy:", round(acc, 5))

    P_a = np.sum(cm, 0)[0] / np.sum(np.sum(cm, 0))
    P_1 = np.sum(cm, 1)[0] / np.sum(np.sum(cm, 1))
    P_a1 = P_a * P_1

    P_b = np.sum(cm, 0)[1] / np.sum(np.sum(cm, 0))
    P_2 = np.sum(cm, 1)[1] / np.sum(np.sum(cm, 1))
    P_b2 = P_b * P_2

    P_e = P_a1 + P_b2

    k = (acc - P_e) / (1 - P_e)
    plog("Cohen's kappa coefficient:", round(k, 5))


#=====
# REQUEST BY ATTRIBUTE
#=====
def request_by_attribute(layer, attr_name, attr_value):
    """Request the features with attr_value and geom intersection."""
    req = QgsFeatureRequest()
    req.setFilterExpression(f'"{attr_name}" = \'{attr_value}\'')

    requested_layer = layer.materialize(req)

    return requested_layer


#=====
# REQUEST BY INTERSECTION
#=====
def request_by_intersection(layer, geom, crs):
    """Request the features with attr_value and geom intersection."""
    context = QgsProject.instance().transformContext()

    req = QgsFeatureRequest()
    req.setDistanceWithin(geometry=geom, distance=0)
    req.setDestinationCrs(crs, context)

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

