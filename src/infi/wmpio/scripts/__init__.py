
MPIO_WMI_NAMESPACE = r'root\wmi'
DEVICES_QUERY = 'SELECT * FROM MPIO_GET_DESCRIPTOR'

from bunch import Bunch

class MpioGetDescriptorEntry(Bunch):
    def __init__(self):
        super(MpioGetDescriptorEntry, self).__init__()
        self.DeviceName = None
        self.InstanceName = None
        self.NumberPdos = None

def travel():
    from wmi import WMI
    client = WMI(namespace=MPIO_WMI_NAMESPACE, find_classes=False)
    query = client.query(DEVICES_QUERY)
    results = []
    for device in query:
        item = MpioGetDescriptorEntry()
        for attr in ['DeviceName', 'InstanceName', 'NumberPdos']:
            setattr(item, attr, getattr(device, attr))
        results.append(item)
    return results
