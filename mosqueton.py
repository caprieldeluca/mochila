# -*- coding: utf-8 -*-

from pathlib import PurePath
import runpy
import sys
import traceback


pkg_path = str(PurePath(__file__).parent)
pkg_name = 'mochila'

# Insert pkg_path at the front of sys.path
if not pkg_path in sys.path:
    sys.path.insert(0, pkg_path)

# Remove all 'pkg_name*' entries from sys.modules to force reload
for k in list(sys.modules.keys()):
    if k.startswith(pkg_name):
        del sys.modules[k]

# Import the package
try:
    runpy.run_path(
        path_name=pkg_path,
        init_globals={
            'plog': plog, # plog comes from puentes plugin
            'pkg_path': pkg_path,
            'pkg_name': pkg_name},
        run_name=pkg_name)

except Exception as e:
    plog(*traceback.format_exception(e, limit=-1))

