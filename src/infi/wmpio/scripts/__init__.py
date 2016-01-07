from __future__ import print_function
__import__("pkg_resources").declare_namespace(__name__)

from sys import argv
from .. import get_multipath_devices, get_load_balace_policies, WmiClient

def walk_on_devices(wmi_client, walk_on_paths, read_all_attributes):
    devices = get_multipath_devices(wmi_client)
    for _, v in devices.items():
        if walk_on_paths:
            for pdo in v.PdoInformation:
                if not read_all_attributes:
                    continue
                _ = pdo.PathIdentifier, pdo.DeviceState,
                _ = pdo.ScsiAddress.Lun, pdo.ScsiAddress.PortNumber, \
                    pdo.ScsiAddress.ScsiPathId, pdo.ScsiAddress.TargetId
        if not read_all_attributes:
            continue
        _ = v.InstanceName, v.DeviceName

def walk_on_policies(wmi_client, walk_on_paths, read_all_attributes):
    policies = get_load_balace_policies(wmi_client)
    for _, v in policies.items():
        if walk_on_paths:
            for path in v.DSM_Paths:
                if not read_all_attributes:
                    continue
                _ = path.DsmPathId, path.FailedPath, path.OptimizedPath, \
                    path.PreferredPath, path.PrimaryPath, path.SymmetricLUA, \
                    path.TargetPort_Identifier, path.TargetPortGroup_Identifier, \
                    path.TargetPortGroup_Preferred, path.TargetPortGroup_State
        if not read_all_attributes:
            continue
        _ = v.InstanceName, v.LoadBalancePolicy

def walk(count, subtree, read_all):
    wmi_client = WmiClient()
    for _ in range(int(count)):
        walk_on_devices(wmi_client, subtree, read_all)
        walk_on_policies(wmi_client, subtree, read_all)

def travel(argv=argv):
    from time import clock
    count, subtree, read_all = argv[1:]
    start_time = clock()
    walk(int(count), int(subtree), int(read_all))
    duration = clock() - start_time
    print(("time=%.2f, iters=%d, iters/sec: %.2f" %
          (duration, int(count), float(count) / duration)))

def profile(argv=argv):
    from cProfile import run
    count, subtree, read_all = argv[1:]
    filename = '.'.join(argv)
    print(filename)
    run("from infi.wmpio.scripts import walk; walk(%s, %s, %s)" % \
        (int(count), int(subtree), int(read_all)), filename)
