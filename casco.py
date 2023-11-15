# -*- coding: utf-8 -*-


from pathlib import PurePath

from mochila import plog
from mochila.vector import confusion_matrix
from mochila.vector import layers


confusion_matrix.test()

# Get results layer
# utf8_path = str(PurePath(__file__).parent / 'vector' / 'data' / 'classification' / 'results.gpkg')
# baseName = 'results'
# results = layers.get_layer_from_gpkg(utf8_path, baseName)

# layer = layers.get_current_layer()

# g = confusion_matrix.get_ref_geom(layer)
# plog(g.asWkt(1))

