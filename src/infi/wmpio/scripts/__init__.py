
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
        self.Identifier = None
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
        self.DsmPathId = None
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

def get_devices(client, query_func_name):
    query_func = client.query if query_func_name == 'query' else 'ExecQuery'
    query = query_func(DEVICES_QUERY)
    devices = {}
    for result in query:
        device = Device()
        for attr in ['DeviceName', 'InstanceName', 'NumberPdos']:
            setattr(device, attr, getattr(result, attr))
            for pdo in result.PdoInformation:
                path = Path()
                for attr in ['DeviceState', 'Identifier', 'PathIdentifier']:
                    setattr(path, attr, getattr(pdo, attr))
                for attr in ['Lun', 'PortNumber', 'ScsiPathId', 'TargetId']:
                    setattr(path.ScsiAddress, attr, getattr(pdo.ScsiAddress, attr))
                device.PdoInformation[path.PathIdentifier] = path
        devices[device.InstanceName] = device
    return devices

def get_policies_for_devices(client, devices, query_func_name):
    query_func = client.query if query_func_name == 'query' else 'ExecQuery'
    query = query_func(LBPOLICY_QUERY)
    for result in query:
        policy = result.LoadBalancePolicy
        device = devices[result.InstanceName]
        device.LoadBalancePolicy = policy.LoadBalancePolicy
        for dsm_path in policy.DSM_Paths:
            path = device.PdoInformation[dsm_path.DsmPathId]
            for attr in ['DsmPathId', 'FailedPath', 'OptimizedPath', 'PathWeight',
                         'PreferredPath', 'PrimaryPath', 'SymmetricLUA',
                         'TargetPort_Identifier', 'TargetPortGroup_Identifier',
                         'TargetPortGroup_Preferred', 'TargetPortGroup_State']:
                setattr(path, attr, getattr(dsm_path, attr))


def wmi_no_find_classes(find_classes=False):
    from wmi import WMI
    client = WMI(namespace=MPIO_WMI_NAMESPACE, find_classes=find_classes)
    devices = get_devices(client, 'query')
    get_policies_for_devices(client, devices, 'query')

def wmi_find_classes():
    wmi_no_find_classes(True)

def win32com_client():
    from win32com.client import GetObject
    client = GetObject('winmgmts:%s' % MPIO_WMI_NAMESPACE)
    devices = get_devices(client, 'ExecQuery')
    get_policies_for_devices(client, devices, 'ExecQuery')

from sys import argv

def travel(argv=argv):
    from time import clock
    methods = {1: wmi_no_find_classes,
               2:wmi_find_classes,
               3:win32com_client }
    method, count = argv[1:]
    start_time = clock()

    for index in range(int(count)):
        methods[int(method)]()
    duration = clock() - start_time
    print("iters=%d, iters/sec: %.2f" % (int(count), float(count) / duration))

