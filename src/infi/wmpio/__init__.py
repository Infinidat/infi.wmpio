__import__("pkg_resources").declare_namespace(__name__)


""" Python bindings to Windows Multipath I/O components.

With this module, you can:
* get information about the connected MPIO devices
* query/add/remove the "Multipath I/O" feature
* query/add/remove claiming rules for the MSDSM
"""

from .wmi import WmiClient, get_multipath_devices, get_load_balace_policies, get_device_performance
from .mpclaim import MultipathClaim
