# -*- coding: utf-8 -*-

import pathlib

def append_stem(utf8_path, stem_part):
    """Append a stem part to a path."""
    p = pathlib.Path(utf8_path)
    old_stem = p.stem
    new_stem = old_stem + stem_part
    return p.with_stem(new_stem)
