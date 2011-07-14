
MPIO_WMI_NAMESPACE = r'root\wmi'
DEVICES_QUERY = 'SELECT * FROM MPIO_GET_DESCRIPTOR'
LBPOLICY_QUERY = 'SELECT * FROM DSM_QueryLBPolicy_V2'

from bunch import Bunch

class MpioGetDescriptorEntry(Bunch):
    def __init__(self):
        super(MpioGetDescriptorEntry, self).__init__()
        self.DeviceName = None
        self.InstanceName = None
        self.NumberPdos = None

class PseudoDeviceObject(Bunch):
    def __init__(self):
        super(PseudoDeviceObject, self).__init__()
        self.DeviceState = None
        self.Identifier = None
        self.PathIdentifier = None
        self.ScsiAddress = None

class ScsiAddress(Bunch):
    def __init__(self):
        super(ScsiAddress, self).__init__()
        self.Lun = None
        self.PortNumber = None
        self.ScsiPathId = None
        self.TargetId = None

def _travel_devices(client):
    query = client.query(DEVICES_QUERY)
    results = []
    for device in query:
        descriptor = MpioGetDescriptorEntry()
        for attr in ['DeviceName', 'InstanceName', 'NumberPdos']:
            setattr(descriptor, attr, getattr(device, attr))
            for path in device.PdoInformation:
                pdo = PseudoDeviceObject()
                pdo.ScsiAddress = ScsiAddress()
                for attr in ['DeviceState', 'Identifier', 'PathIdentifier']:
                    setattr(pdo, attr, getattr(path, attr))
                for attr in ['Lun', 'PortNumber', 'ScsiPathId', 'TargetId']:
                    setattr(pdo.ScsiAddress, attr, getattr(path.ScsiAddress, attr))

        results.append(descriptor)
    return results

def _travel_policies(client):
    query = client.query(LBPOLICY_QUERY)
    return []

def travel():
    from wmi import WMI
    client = WMI(namespace=MPIO_WMI_NAMESPACE, find_classes=False)
    devices = _travel_devices(client)
    return devices
