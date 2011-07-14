
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
        self.PrefferedPath = None
        self.PrimaryPath = None
        self.SymmetricLUA = None
        self.TargetPort_Identifier = None
        self.TargetPortGroup_Identifier = None
        self.TargetPortGroup_Preferred = None
        self.TargetPortGroup_State = None

def get_devices(client):
    query = client.query(DEVICES_QUERY)
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

def get_policies_for_devices(client, devices):
    query = client.query(LBPOLICY_QUERY)
    for result in query:
        policy = result.LoadBalancePolicy
        device = devices[result.InstanceName]
        device.LoadBalancePolicy = policy.LoadBalancePolicy
        for dsm_path in policy.DSM_Paths:
            path = device.PdoInformation[dsm_path.DsmPathId]
            for attr in ['DsmPathId', 'FailedPath', 'OptimizedPath', 'PathWeight',
                         'PrefferedPath', 'PrimaryPath', 'SymmetricLUA',
                         'TargetPort_Identifier', 'TargetPortGroup_Identifier',
                         'TargetPortGroup_Preferred', 'TargetPortGroup_State']:
                setattr(path, attr, getattr(dsm_path, attr))

def travel():
    from wmi import WMI
    client = WMI(namespace=MPIO_WMI_NAMESPACE, find_classes=False)
    devices = get_devices(client)
    get_policies_for_devices(client, devices)
    print devices
    return devices
