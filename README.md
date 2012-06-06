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

This project uses buildout, and git to generate setup.py and __version__.py.
In order to generate these, run:

    python -S bootstrap.py -d -t
    bin/buildout -c buildout-version.cfg
    python setup.py develop

In our development environment, we use isolated python builds, by running the following instead of the last command:

    bin/buildout install development-scripts

