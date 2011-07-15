__import__("pkg_resources").declare_namespace(__name__)

import sys
from os.path import join, dirname, abspath

COMTYPES_MODULE = abspath(join(dirname(__file__), "comtypes"))

if COMTYPES_MODULE not in sys.path:
    sys.path.append(COMTYPES_MODULE)
