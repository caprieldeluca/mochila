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

src_path = this_path / 'raster' / 'single_view' / 'data' / 'DJI_0173.JPG'
src_utf8_path = str(src_path)

dst_path = src_path.parent / 'rectified' / f'{src_path.stem}_rect.TIF'
dst_utf8_path = str(dst_path)


corrections = {
    'DELTA_ROLL': -5.00,
    'DELTA_PITCH': 8.00,
    'DELTA_YAW': -2,
    'DELTA_ALT': 0.00
}

main.process(src_utf8_path, dst_utf8_path, corrections=corrections)

