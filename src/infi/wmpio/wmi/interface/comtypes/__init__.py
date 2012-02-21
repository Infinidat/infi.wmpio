__import__("pkg_resources").declare_namespace(__name__)

import sys
from os.path import dirname, abspath

COMTYPES_MODULE = abspath(dirname(__file__))

if COMTYPES_MODULE not in sys.path:
    for module in filter(lambda path: 'comtypes' in path, sys.path):
        sys.path.remove(module)
    sys.path.append(COMTYPES_MODULE)

