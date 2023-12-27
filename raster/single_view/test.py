# -*- coding: utf-8 -*-

from pathlib import Path
from datetime import datetime

from mochila import plog
from mochila.raster.single_view import main

def test():
    """Test the process function with sample data."""

    this_path = Path(__file__).parent.resolve()

    src_path = this_path / 'data' / 'DJI_0173.JPG'
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

    plog(f'{datetime.now() = }')
