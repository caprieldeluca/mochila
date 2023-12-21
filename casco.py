# -*- coding: utf-8 -*-


from pathlib import Path

from mochila import plog
from mochila.vector import confusion_matrix
from mochila.vector import vlayers
from mochila.raster import rlayers
from mochila.raster.single_view import (
    metadata,
    main
)

layer = None

this_path = Path(__file__).parent.resolve()

uri = str(this_path / 'raster' / 'single_view' / 'data' / 'DJI_0173.JPG')
baseName = 'DJI_0173'
plog(f'{uri = }')

corrections = {
    'DELTA_ROLL': -5.00,
    'DELTA_PITCH': 8.00,
    'DELTA_YAW': 2,
    'DELTA_ALT': 5.00
}

main.process(uri, corrections)
