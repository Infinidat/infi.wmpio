__import__("pkg_resources").declare_namespace(__name__)

from .wmi import WmiObject, WmiClient

MPIO_WMI_NAMESPACE = r'root\wmi'
DEVICES_QUERY = 'SELECT * FROM MPIO_GET_DESCRIPTOR'
LBPOLICY_QUERY = 'SELECT * FROM DSM_QueryLBPolicy_V2'

class Device(WmiObject):
    def __init__(self, com_object):
        super(Device, self).__init__(com_object)
        self._PdoInformation = []

    @property
    def DeviceName(self):
        return self.get_wmi_attribute("DeviceName")

    @property
    def InstanceName(self):
        return self.get_wmi_attribute("InstanceName")

    @property
    def PdoInformation(self):
        if len(self._PdoInformation):
            for path in self._PdoInformation:
                yield path
        else:
            items = self.get_wmi_attribute("PdoInformation")
            for item in items:
                path = PdoInformation(item)
                self._PdoInformation.append(path)
                yield path

class PdoInformation(WmiObject):
    def __init__(self, com_object):
        super(PdoInformation, self).__init__(com_object)
        self._ScsiAddress = None

    @property
    def DeviceState(self):
        return self.get_wmi_attribute("DeviceState")

    @property
    def PathIdentifier(self):
        return self.get_wmi_attribute("PathIdentifier")

    @property
    def ScsiAddress(self):
        if self._ScsiAddress is None:
            self._ScsiAddress = ScsiAddress(self.get_wmi_attribute("ScsiAddress"))
        return self._ScsiAddress

class ScsiAddress(WmiObject):
    @property
    def Lun(self):
        return self.get_wmi_attribute("Lun")

    @property
    def PortNumber(self):
        return self.get_wmi_attribute("PortNumber")

    @property
    def ScsiPathId(self):
        return self.get_wmi_attribute("ScsiPathId")

    @property
    def TargetId(self):
        return self.get_wmi_attribute("TargetId")

class LoadBalancePolicy(WmiObject):
    def __init__(self, com_object, instance_name):
        super(LoadBalancePolicy, self).__init__(com_object)
        self._DSM_Paths = []
        self.InstanceName = instance_name

    @property
    def DSM_Paths(self):
        if len(self._DSM_Paths):
            for path in self._DSM_Paths:
                yield path
        else:
            items = self.get_wmi_attribute("DSM_Paths")
            for item in items:
                path = DSM_Path(item)
                self._DSM_Paths.append(path)
                yield path
    @property
    def LoadBalancePolicy(self):
        return self.get_wmi_attribute("LoadBalancePolicy")

class DSM_Path(WmiObject):
    @property
    def DsmPathId(self):
        return self.get_wmi_attribute("DsmPathId")

    @property
    def FailedPath(self):
        return self.get_wmi_attribute("FailedPath")

    @property
    def OptimizedPath(self):
        return self.get_wmi_attribute("OptimizedPath")

    @property
    def PathWeight(self):
        return self.get_wmi_attribute("PathWeight")

    @property
    def PreferredPath(self):
        return self.get_wmi_attribute("PreferredPath")

    @property
    def PrimaryPath(self):
        return self.get_wmi_attribute("PrimaryPath")

    @property
    def SymmetricLUA(self):
        return self.get_wmi_attribute("SymmetricLUA")

    @property
    def TargetPort_Identifier(self):
        return self.get_wmi_attribute("TargetPort_Identifier")

    @property
    def TargetPortGroup_Identifier(self):
        return self.get_wmi_attribute("TargetPortGroup_Identifier")

    @property
    def TargetPortGroup_Preferred(self):
        return self.get_wmi_attribute("TargetPortGroup_Preferred")

    @property
    def TargetPortGroup_State(self):
        return self.get_wmi_attribute("TargetPortGroup_State")

def get_mulitpath_devices(wmi_client):
    devices = dict()
    for result in wmi_client.execute_query(DEVICES_QUERY):
        device = Device(result)
    devices[device.InstanceName] = device
    return devices

def get_load_balace_policies(wmi_client):
    policies = dict()
    for result in wmi_client.execute_query(LBPOLICY_QUERY):
        wmi_object = WmiObject(result)
        instance_name = wmi_object.get_wmi_attribute("InstanceName")
        policies[instance_name] = LoadBalancePolicy(
                    wmi_object.get_wmi_attribute("LoadBalancePolicy"),
                    instance_name)
    return policies
