Overview
========
Python bindings to Windows MPIO management, via WMI and mpclaim.exe

Usage
-----

```python
>>> from infi.wmpio import WmiClient, MultipathClaim, get_multipath_devices
>>> device_names = [device.DeviceName for device in get_multipath_devices(WmiClient())]
>>> MultipathClaim.claim_discovered_hardware(spc3_only=True)
```

Checking out the code
=====================

To check out the code for development purposes, clone the git repository and run the following commands:

    easy_install -U infi.projector
    projector devenv build

Python 3
========
Python 3 support is experimental and untested at this stage.
