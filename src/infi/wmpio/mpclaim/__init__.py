
def is_windows_2008():
    if MultipathClaim._windows_2008 is None:
        from infi.winver import Windows
        MultipathClaim._windows_2008 = Windows().is_windows_2008()
    return MultipathClaim._windows_2008


CLEAR_POLICY = 0
FAIL_OVER_ONLY = 1
ROUND_ROBIN = 2
ROUND_ROBIN_WITH_SUBSET = 3
LEAST_QUEUE_DEPTH = 4
WEIGHTED_PATHS = 5
LEAST_BLOCKS = 6

ACTIVE_OPTIMIZED = 0
ACTIVE_NON_OPTIMIZED = 1
STANDBY = 2
UNAVAILABLE = 3

class MultipathClaim(object):
    """ wrapper to the mpclaim.exe utility
    This class only wraps functiontonality that we cannot retreive programatically through WMI
    """

    _windows_2008_r2 = None
    _windows_2008 = None

    @classmethod
    def path(cls):
        """ returns the path of mpclaim.exe
        """
        from os.path import sep, join, exists
        from os import environ
        return join(environ.get("SystemRoot", join("C:", sep, "Windows")), "System32", "mpclaim.exe")

    @classmethod
    def execute(cls, commandline_arguments, check_return_code=True):
        """ executes mpclaim.exe with the command-line arguments.
        if mpclaim's return value is non-zero, a RuntimeError exception is raised with stderr
        """
        from infi.execute import execute
        from logging import debug
        arguments = [cls.path()]
        arguments.extend(commandline_arguments)
        process = execute(arguments)
        process.wait()
        if process.get_returncode() != 0 and check_return_code:
            raise RuntimeError(arguments, process.get_returncode(), process.get_stdout(), process.get_stderr())
        return process.get_stdout()

    @classmethod
    def _get_hardware_id(cls, vendor_id, product_id):
        """ returns the concatination of vendor_id and product_id, both justed
        """
        return "%s%s" % (vendor_id.ljust(8), product_id.ljust(16))

    @classmethod
    def _create_mpdev_key_if_missing(cls):
        from infi.registry import LocalComputer, RegistryValueFactory
        from infi.registry.constants import KEY_READ, KEY_WRITE, KEY_ENUMERATE_SUB_KEYS, KEY_QUERY_VALUE, REG_MULTI_SZ

        MPDEV_KEY_PATH = r'SYSTEM\CurrentControlSet\Control\MPDEV'

        registry = LocalComputer(KEY_READ | KEY_WRITE | KEY_ENUMERATE_SUB_KEYS | KEY_QUERY_VALUE)
        if registry.local_machine.get(MPDEV_KEY_PATH) is None:
            registry.local_machine[MPDEV_KEY_PATH] = ''
        if registry.local_machine[MPDEV_KEY_PATH].values_store.get('MPIOSupportedDeviceList') is None:
            mpdev_key = registry.local_machine[MPDEV_KEY_PATH]
            mpdev_key.values_store['MPIOSupportedDeviceList'] = RegistryValueFactory().by_type(REG_MULTI_SZ)([''])

    @classmethod
    def claim_specific_hardware(cls, vendor_id, product_id):
        """ tells mpio to claim a specific hardware
        """
        cls._create_mpdev_key_if_missing()
        cls.execute(["-n", "-i", "-d", cls._get_hardware_id(vendor_id, product_id)],
                    not is_windows_2008())

    @classmethod
    def claim_discovered_hardware(cls, spc3_only=False):
        """ tells mpio to claim disks of all attached hardware types
        if spc3_only is True, it has claim only disks that are spc3-complaint
        """
        cls.execute(["-n", "-i", "-c" if spc3_only else "-a", ' '], not is_windows_2008())

    @classmethod
    def is_hardware_claimed(cls, vendor_id, product_id):
        """ returns True if the specific hardware is claimed by mpio
        """
        return dict(vendor_id=vendor_id, product_id=product_id) in cls.get_claimed_hardware()

    @classmethod
    def unclaim_all_hardware(cls):
        cls.execute(["-n", "-u", "-a", ' '], not is_windows_2008())

    @classmethod
    def unclaim_specific_hardware(cls, vendor_id, product_id):
        if not cls.is_hardware_claimed(vendor_id, product_id):
            return #pragma: no-cover
        cls.execute(["-n", "-u", "-d", cls._get_hardware_id(vendor_id, product_id)],
                     not is_windows_2008())

    @classmethod
    def get_claimed_hardware(cls):
        """ returns a list of two-key dictionaries: vendor_id, hardware_id, of stuff claimed by mpio
        """
        from infi.registry import LocalComputer
        from infi.registry.constants import KEY_READ, KEY_ENUMERATE_SUB_KEYS, KEY_QUERY_VALUE

        registry = LocalComputer(KEY_READ | KEY_ENUMERATE_SUB_KEYS | KEY_QUERY_VALUE)
        try:
            mpdev = registry.local_machine[r'SYSTEM\CurrentControlSet\Control\MPDEV']
            devices_list = mpdev.values_store['MPIOSupportedDeviceList'].to_python_object()
        except KeyError:
            devices_list = []
        return [dict(vendor_id=device[:8], product_id=device[8:]) for device in devices_list]

    @classmethod
    def _extract_load_balancing_from_output(cls, output):
        if "MSDSM-wide Load Balance Policy: Fail Over Only" in output:
            return FAIL_OVER_ONLY
        if "MSDSM-wide Load Balance Policy: Round Robin" in output:
            return ROUND_ROBIN
        if "MSDSM-wide Load Balance Policy: Least Queue Depth" in output:
            return LEAST_QUEUE_DEPTH
        if "MSDSM-wide Load Balance Policy: Least Blocks" in output:
            return LEAST_BLOCKS
        return CLEAR_POLICY

    @classmethod
    def _extract_hardware_specific_load_balacing_policy(cls, output, hardware_id):
        if hardware_id not in output:
            return CLEAR_POLICY

        for line in output.splitlines():
            if hardware_id not in line:
                continue
            break

        policy_string = line.split()[-1]
        if policy_string == "RR":
            return ROUND_ROBIN
        if policy_string == "FOO":
            return FAIL_OVER_ONLY
        if policy_string == "LQD":
            return LEAST_QUEUE_DEPTH
        if policy_string == "LB":
            return LEAST_BLOCKS

    @classmethod
    def get_default_load_balancing_policy(cls):
        """ returns MSDSM's default load balancing policy
        """
        output = cls.execute(["-s", "-m"])
        return cls._extract_load_balancing_from_output(output)

    @classmethod
    def set_default_load_balancing_policy(cls, policy):
        """ sets MSDSM's default load balancing policy
        """
        cls.execute(["-l", "-m", str(policy)])

    @classmethod
    def get_hardware_specific_load_balancing_poicy(cls, vendor_id, product_id):
        """ gets MSDSM's explicit load balancing policy for a given hardware type
        if no such policy exists, CLEAR_POLICY is returns, and NOT the global-wise policy
        """
        output = cls.execute(["-s", "-t"])
        hardware_id = cls._get_hardware_id(vendor_id, product_id)
        return cls._extract_hardware_specific_load_balacing_policy(output, hardware_id)

    @classmethod
    def set_hardware_specific_load_balancing_policy(cls, vendor_id, product_id, policy):
        """ sets a load balancing policy explicitly for a given hardware type
        """
        cls.execute(["-l", "-t", cls._get_hardware_id(vendor_id, product_id), str(policy)])

    @classmethod
    def set_device_specific_load_balancing_policy(cls, device, load_balance_policy):
        """ sets an explicit load balancing policy for a given device
        this method accepts a Device and LoadBalancePolicy objects, and sets
        whatever policy and states that are defined in these objects.

        The LoadBalancePolicy attribute is taken from LoadBalancePolicy.LoadBalancePolicy
        The DeviceState attribute is taked for the paths in Device.PdoInformation
        The PreferredPath and PathWeight attribures are taken for the paths in LoadBalancePolicy.Dsm_Paths

        For clearing the explicit policy, or setting round-robin, least-queue-depth, least-blocks,
        we ignore the state of the paths.
        For setting round-robin-with-subset and weighted paths, we use the device states as they are now, and
        override their TPG state.
        """
        assert device.InstanceName == load_balance_policy.InstanceName
        disk_number = device.DeviceName.split("MPIODisk")[-1]
        policy = load_balance_policy.LoadBalancePolicy
        paths = dict()
        for path in device.PdoInformation:
            paths[path.PathIdentifier] = dict(DeviceState=path.DeviceState)
        for path in load_balance_policy.DSM_Paths:
            for attr in ["PreferredPath", "PathWeight"]:
                paths[path.DsmPathId][attr] = getattr(path, attr)
        if policy in [CLEAR_POLICY, ROUND_ROBIN, LEAST_QUEUE_DEPTH, LEAST_BLOCKS]:
            cls.execute(["-l", "-d", str(disk_number), str(policy)])
        else:
            paths_parameters = []
            for key, value in paths.items():
                paths_parameters.extend([hex(int(key))[2:].zfill(16),
                                         str(value["DeviceState"]),
                                         str(value["PathWeight"]),
                                         str(value["PreferredPath"])])
            cls.execute(["-l", "-d", str(disk_number), str(policy)] + paths_parameters)
