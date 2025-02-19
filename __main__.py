# -*- coding: utf-8 -*-
import importlib.util
import os

# Variables provided by mosqueton.py
__path__ = [pkg_path]
__package__ = pkg_name

# Get the absolute path of CASCO
casco_path = os.getenv("CASCO", None)

if casco_path and os.path.exists(casco_path):
    # Load casco.py from the specified CASCO path
    spec = importlib.util.spec_from_file_location("casco", casco_path)
    casco = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(casco)
else:
    # If CASCO is not defined, import the default casco.py from mochila
    from mochila import casco
