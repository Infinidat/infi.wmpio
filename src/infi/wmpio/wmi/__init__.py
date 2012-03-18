__import__("pkg_resources").declare_namespace(__name__)

from infi.wmi import WmiObject
from infi.wmi import WmiClient as WmiClient_
from .model import Device, LoadBalancePolicy, DEVICES_QUERY, LBPOLICY_QUERY

class WmiClient(WmiClient_):
    def __init__(self):
        super(WmiClient, self).__init__(r"root\wmi")


def get_multipath_devices(wmi_client):
    """ returns a dictionary of (Device.InstanceName, Device) items
    """
    devices = dict()
    for result in wmi_client.execute_query(DEVICES_QUERY):
        device = Device(result)
        devices[device.InstanceName] = device
    return devices

def get_load_balace_policies(wmi_client):
    """ returns a dictionary of (LoadBalanePolicy.InstanceName, LoadBalancePolicy)
    items """
    policies = dict()
    for result in wmi_client.execute_query(LBPOLICY_QUERY):
        wmi_object = WmiObject(result)
        instance_name = wmi_object.get_wmi_attribute("InstanceName")
        policies[instance_name] = LoadBalancePolicy(wmi_object.get_wmi_attribute("LoadBalancePolicy"),
                                                    instance_name)
    return policies

