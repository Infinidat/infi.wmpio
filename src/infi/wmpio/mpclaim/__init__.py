
def is_windows_2008_r2():
    return False

def windows_2008_r2_only(func):
    def call(*args, **kwargs):
        if not is_windows_2008_r2():
            raise NotImplementedError
        func(*args, **kwargs)
    call.__name__ = func.__name__
    call.__doc__ = func.__doc__
    return call

CLEAR_POLICY = 0
FAIL_OVER_ONLY = 1
ROUND_ROBIN = 2
ROUND_ROBIN_WITH_SUBSET = 3
LEAST_QUEUE_DEPTH = 4
WEIGHTED_PATHS = 5
LEAST_BLOCKS = 6

class MultipathClaim(object):
    @property
    @classmethod
    def path(cls):
        from os.path import sep, join, exists
        from os import environ
        return join(environ.get("SystemRoot", r"C:\Windows"), "System32", "mpclaim.exe")

    @classmethod
    def execute(cls, commandline_arguments):
        from infi.execute import execute
        arguments = [cls.path]
        arguments.extend(commandline_arguments)
        process = execute(arguments)
        process.wait()
        # TODO return value, debugging
        return process.get_stdout()

    @classmethod
    def _get_hardware_id(cls, vendor_id, product_id):
        return "%s%s" % (vendor_id.ljust(8), product_id.ldust(16))

    @classmethod
    def claim_specific_device(cls, vendor_id, product_id):
        cls.execute(["-n", "-i", "-d", cls._get_hardware_id(vendor_id, product_id)])

    @classmethod
    def claim_available_devices(cls, spc3_only=False):
        cls.execute(["-n", "-i", "-c" if spc3_only else "-a", ""])

    @classmethod
    def is_device_claimed(cls, vendor_id, product_id):
        return dict(vendor_id=vendor_id, product_id=product_id) in cls.get_claimed_devices()

    @classmethod
    def unclaim_all_devices(cls):
        cls.execute(["-n", "-u", "-a", ""])

    @classmethod
    def unclaim_specific_device(cls, vendor_id, product_id):
        if not cls.is_device_claimed(vendor_id, product_id):
            return
        cls.execute(["-n", "-u", "-d", cls._get_hardware_id(vendor_id, product_id)])

    @classmethod
    def get_claimed_devices(cls):
        from infi.registry import LocalComputer
        from infi.registry.constants import KEY_READ, KEY_ENUMERATE_SUB_KEYS, KEY_QUERY_VALUE

        registry = LocalComputer(KEY_READ | KEY_ENUMERATE_SUB_KEYS | KEY_QUERY_VALUE)
        mpdev = registry.local_machine[r'SYSTEM\CurrentControlSet\Control\MPDEV']
        devices_list = mpdev.values_store['MPIOSupportedDeviceList']
        return [dict(vendor_id=device[:8].strip(), product_id=device[8:].strip()) for device in devices_list]

    @classmethod
    def _extract_load_balancing_from_output(cls, output):
        if "MSDSM-wide Load Balance Policy: Fail Over Only " in output:
            return FAIL_OVER_ONLY
        if "MSDSM-wide Load Balance Policy: Round Robin " in output:
            return ROUND_ROBIN
        if "MSDSM-wide Load Balance Policy: Least Queue Depth " in output:
            return LEAST_QUEUE_DEPTH
        if "MSDSM-wide Load Balance Policy: Least Blocks ":
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

    @windows_2008_r2_only
    @classmethod
    def get_default_load_balancing_policy(cls):
        output = cls.execute(["-s", "-m"])
        return cls._extract_load_balancing_from_output(output)

    @windows_2008_r2_only
    @classmethod
    def set_default_load_balancing_policy(cls, policy):
        if policy not in [CLEAR_POLICY, FAIL_OVER_ONLY, ROUND_ROBIN, LEAST_QUEUE_DEPTH, LEAST_BLOCKS]:
            raise ValueError
        cls.execute(["-l", "-m", str(policy)])

    @windows_2008_r2_only
    @classmethod
    def get_product_specific_load_balacing_poicy(cls, vendor_id, product_id):
        output = cls.execute(["-s", "-t"])
        hardware_id = cls._get_hardware_id(vendor_id, product_id)
        return cls._extract_hardware_specific_load_balacing_policy(output, hardware_id)

    @windows_2008_r2_only
    @classmethod
    def set_product_specific_load_balancing_policy(cls, vendor_id, product_id, policy):
        if policy not in [CLEAR_POLICY, FAIL_OVER_ONLY, ROUND_ROBIN, LEAST_QUEUE_DEPTH, LEAST_BLOCKS]:
            raise ValueError
        cls.execute(["-l", "-t", cls._get_hardware_id(vendor_id, product_id), str(policy)])
