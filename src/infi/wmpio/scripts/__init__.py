
MPIO_WMI_NAMESPACE = r'root\wmi'
DEVICES_QUERY = 'SELECT * FROM MPIO_GET_DESCRIPTOR'
LBPOLICY_QUERY = 'SELECT * FROM DSM_QueryLBPolicy_V2'

from bunch import Bunch

class Device(Bunch):
    def __init__(self):
        super(Device, self).__init__()
        self.DeviceName = None
        self.InstanceName = None
        self.LoadBalancePolicy = None
        self.PdoInformation = dict()

class Path(Bunch):
    def __init__(self):
        super(Path, self).__init__()
        self.DeviceState = None
        self.PathIdentifier = None
        self.ScsiAddress = ScsiAddress()

class ScsiAddress(Bunch):
    def __init__(self):
        super(ScsiAddress, self).__init__()
        self.Lun = None
        self.PortNumber = None
        self.ScsiPathId = None
        self.TargetId = None

class LoadBalancePolicy(Bunch):
    def __init__(self):
        super(LoadBalancePolicy, self).__init__()
        self.FailedPath = None
        self.OptimizedPath = None
        self.PathWeight = None
        self.PreferredPath = None
        self.PrimaryPath = None
        self.SymmetricLUA = None
        self.TargetPort_Identifier = None
        self.TargetPortGroup_Identifier = None
        self.TargetPortGroup_Preferred = None
        self.TargetPortGroup_State = None

def _get_properties(wmi_object):
    return wmi_object.Properties_

def _get_item(property_set, attr):
    return property_set.Item(attr)

def _get_value(item):
    return item.Value

def _wmi_getattr(wmi_object, attr):
    return _get_value(_get_item(_get_properties(wmi_object), attr))

def _exec_query(client, query):
    return client.ExecQuery(query)

def _get_index(results, index):
    return results.ItemIndex(index)

def get_devices(client):
    query = _exec_query(client, DEVICES_QUERY)
    devices = {}
    for device_index in xrange(query.Count):
        result = _get_index(query, device_index)
        device = Device()
        for attr in ['DeviceName', 'InstanceName']:
            setattr(device, attr, _wmi_getattr(result, attr))
        PdoInformation = _wmi_getattr(result, "PdoInformation") # GetBestInterface
        for pdo in PdoInformation:
            path = Path()
            ScsiAddress = _wmi_getattr(pdo, 'ScsiAddress') # GetBestInterface
            for attr in ['DeviceState', 'PathIdentifier']:
                setattr(path, attr, _wmi_getattr(pdo, attr))
            for attr in ['Lun', 'PortNumber', 'ScsiPathId', 'TargetId']:
                #setattr(path.ScsiAddress, attr, _wmi_getattr(ScsiAddress, attr))
                pass
            device.PdoInformation[path.PathIdentifier] = path
        devices[device.InstanceName] = device
    return devices

def get_policies_for_devices(client, devices):
    query = _exec_query(client, LBPOLICY_QUERY)
    for index in xrange(query.Count):
        result = _get_index(query, index)
        policy = _wmi_getattr(result, 'LoadBalancePolicy')
        device = devices[_wmi_getattr(result, 'InstanceName')]
        device.LoadBalancePolicy = _wmi_getattr(policy, 'LoadBalancePolicy') # GetBestInterface
        for dsm_path in _wmi_getattr(policy, 'DSM_Paths'):
            path = device.PdoInformation[_wmi_getattr(dsm_path, 'DsmPathId')] # GetBestInterface
            for attr in ['FailedPath', 'OptimizedPath', 'PathWeight',
                         'PreferredPath', 'PrimaryPath', 'SymmetricLUA',
                         'TargetPort_Identifier', 'TargetPortGroup_Identifier',
                         'TargetPortGroup_Preferred', 'TargetPortGroup_State']:
                #setattr(path, attr, _wmi_getattr(dsm_path, attr))
                pass

def wmi_method(find_classes):
    from wmi import WMI
    client = WMI(namespace=MPIO_WMI_NAMESPACE, find_classes=find_classes)
    return client

def wmi_no_find_classes():
    return wmi_method(False)

def wmi_find_classes():
    return wmi_method(True)

def _generate_wmi_early_binding():
    from win32com.client import gencache
    gencache.EnsureModule('{565783C6-CB41-11D1-8B02-00600806D9B6}', 0, 1, 2)

def win32com_client():
    _generate_wmi_early_binding()
    from win32com.client import GetObject
    client = GetObject('winmgmts:%s' % MPIO_WMI_NAMESPACE)
    return client

def comtypes_client():
    from comtypes import CoGetObject
    from comtypes.client import GetModule
    wmi_module = GetModule(['{565783C6-CB41-11D1-8B02-00600806D9B6}', 1 , 2 ])
    client = CoGetObject(r"winmgmts:root\wmi", interface=wmi_module.ISWbemServicesEx)
    return client

from sys import argv

import mock

def travel(argv=argv):
    from time import clock
    methods = {
               3:win32com_client,
               4:comtypes_client}
    method, count = argv[1:]
    start_time = clock()

    client = methods[int(method)]()
    for index in range(int(count)):
        devices = get_devices(client)
        get_policies_for_devices(client, devices)
    duration = clock() - start_time
    print("time=%.2f, iters=%d, iters/sec: %.2f" %
          (duration, int(count), float(count) / duration))

def profile(argv=argv):
    from cProfile import run
    filename = '.'.join(argv)
    print filename
    run("from infi.wmpio.scripts import travel; travel(%s)" % argv, filename)


