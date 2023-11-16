# -*- coding: utf-8 -*-


from pathlib import PurePath

from mochila import plog
from mochila.vector import confusion_matrix
from mochila.vector import layers


# confusion_matrix.test()

# Get results layer
# utf8_path = str(PurePath(__file__).parent / 'vector' / 'data' / 'classification' / 'results.gpkg')
# baseName = 'results'
samples = layers.get_layer_by_name('Eval_Delta')
results = layers.get_layer_by_name('DeltaNov13')
attr_name = 'Bosque'
plog("*" * 20)
plog("Informar Matriz de confusión, exactitud y coeficiente kappa de Cohen para:")
plog("samples='Eval_Delta', results='DeltaNov13', attr_name='Bosque'.")
plog("-"*20)
confusion_matrix.run(samples, results, attr_name)
# layer = layers.get_current_layer()

# g = confusion_matrix.get_ref_geom(layer)
# plog(g.asWkt(1))
samples = layers.get_layer_by_name('Eval_Tdb')
results = layers.get_layer_by_name('TdBNov13')
attr_name = 'BnB'
plog("*" * 20)
plog("Informar Matriz de confusión, exactitud y coeficiente kappa de Cohen para:")
plog("samples='Eval_Tdb', results='TdBNov13', attr_name='BnB'.")
plog("-"*20)
confusion_matrix.run(samples, results, attr_name)
