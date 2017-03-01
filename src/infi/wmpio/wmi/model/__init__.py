
MPIO_WMI_NAMESPACE = r'root\wmi'
DEVICES_QUERY = 'SELECT * FROM MPIO_GET_DESCRIPTOR'
LBPOLICY_QUERY = 'SELECT * FROM DSM_QueryLBPolicy_V2'
MSDSM_DEVICE_PERF_QUERY = 'SELECT * FROM MSDSM_DEVICE_PERF'
DEVICE_PERFORMANCE_QUERY = 'SELECT * FROM MPIO_DEVINSTANCE_HEALTH_INFO'

from .. import WmiObject

class Device(WmiObject):
    def __init__(self, com_object):
        super(Device, self).__init__(com_object)
        self._PdoInformation = []
        self._LoadBalacePolicy = None

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
            if not items:
                return
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

    @DeviceState.setter
    def DeviceState(self, value):
        self._values["DeviceState"] = value

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

    @LoadBalancePolicy.setter
    def LoadBalancePolicy(self, value):
        self._values["LoadBalancePolicy"] = value

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

    @PathWeight.setter
    def PathWeight(self, value):
        self._values["PathWeight"] = value

    @property
    def PreferredPath(self):
        return self.get_wmi_attribute("PreferredPath")

    @PreferredPath.setter
    def PreferredPath(self, value):
        self._values["PreferredPath"] = value

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

class DevicePathPerformance(WmiObject):
    @property
    def PathId(self):
        return int(self.get_wmi_attribute("PathId"))

    @property
    def BytesRead(self):
        return int(self.get_wmi_attribute("NumberBytesRead"))

    @property
    def BytesWritten(self):
        return int(self.get_wmi_attribute("NumberBytesWritten"))

    @property
    def NumberReads(self):
        return int(self.get_wmi_attribute("NumberReads"))

    @property
    def NumberWrites(self):
        return int(self.get_wmi_attribute("NumberWrites"))

class DevicePerformance(WmiObject):
    @property
    def InstanceName(self):
        return self.get_wmi_attribute("InstanceName")

    @property
    def NumberPaths(self):
        return self.get_wmi_attribute("NumberDevInstancePackets")

    @property
    def PerfInfo(self):
        items = self.get_wmi_attribute("DevInstanceHealthPackets")
        paths = dict()
        for item in items:
            path_perf = DevicePathPerformance(item)
            paths[path_perf.PathId] = path_perf
        return paths
