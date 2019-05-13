from infi import unittest
import mock

from . import MultipathClaim
from contextlib import contextmanager
from infi.wmpio.mpclaim import MultipathClaim

from . import CLEAR_POLICY, FAIL_OVER_ONLY, ROUND_ROBIN, ROUND_ROBIN_WITH_SUBSET
from . import LEAST_QUEUE_DEPTH, WEIGHTED_PATHS, LEAST_BLOCKS
from . import ACTIVE_OPTIMIZED, ACTIVE_NON_OPTIMIZED, STANDBY, UNAVAILABLE

class MpclaimTestCase(unittest.TestCase):
    VENDOR_ID = "ABC"
    PRODUCT_ID = "123"
    HARDWARE_ID = VENDOR_ID.ljust(8) + PRODUCT_ID.ljust(16)

    def test_path(self):
        from os.path import join, sep
        self.assertEqual(MultipathClaim.path(),
                         join(join("C:", sep, "Windows"), "System32", "mpclaim.exe"))

    @mock.patch("infi.execute.execute")
    def test_execute__ok(self, execute):
        execute.return_value.get_returncode.return_value = 0
        execute.return_value.get_stdout.return_value = "ok"
        self.assertEqual(MultipathClaim.execute(["something"]), "ok")

    @mock.patch("infi.execute.execute")
    def test_execute__not_ok(self, execute):
        execute.return_value.get_returncode.return_value = 1
        self.assertRaises(RuntimeError, MultipathClaim.execute, *[[], ], **{})

    def test_hardware_id(self):
        self.assertEqual(MultipathClaim._get_hardware_id("NFINIDAT", "InfiniBox"),
                         "NFINIDATInfiniBox       ")
        self.assertEqual(MultipathClaim._get_hardware_id("", ""), " "*24)

    @mock.patch.object(MultipathClaim, "_create_mpdev_key_if_missing")
    @mock.patch.object(MultipathClaim, "execute")
    def test_claim_specific_hardware(self, execute, _create_mpdev_key_if_missing):
        MultipathClaim.claim_specific_hardware(self.VENDOR_ID, self.PRODUCT_ID)
        self.assertEqual(' '.join(execute.call_args[0][0]),
                         ("-n -i -d %s" % self.HARDWARE_ID))

    @mock.patch.object(MultipathClaim, "execute")
    def test_claim_all(self, execute):
        MultipathClaim.claim_discovered_hardware(False)
        self.assertEqual(' '.join(execute.call_args[0][0]),
                         "-n -i %s  " % "-a")

    @mock.patch.object(MultipathClaim, "execute")
    def test_claim_all__spc3_only(self, execute):
        MultipathClaim.claim_discovered_hardware(True)
        self.assertEqual(' '.join(execute.call_args[0][0]),
                         "-n -i %s  " % "-c")

    @mock.patch("infi.wmpio.mpclaim.MultipathClaim.get_claimed_hardware")
    def test_is_hardware_claimed(self, get_claimed_hardware):
        get_claimed_hardware.return_value = [dict(vendor_id="foo", product_id="bar"),
                                            dict(vendor_id="hello", product_id="world"), ]
        self.assertTrue(MultipathClaim.is_hardware_claimed("hello", "world"))
        self.assertTrue(MultipathClaim.is_hardware_claimed("foo", "bar"))

    @mock.patch.object(MultipathClaim, "execute")
    def test_unclaim_all_hardware(self, execute):
        MultipathClaim.unclaim_all_hardware()
        self.assertEqual(' '.join(execute.call_args[0][0]),
                         "-n -u -a  ")

    @mock.patch.object(MultipathClaim, "execute")
    @mock.patch.object(MultipathClaim, "is_hardware_claimed")
    def test_unclaim_specific_hardware(self, is_hardware_claimed, execute):
        is_hardware_claimed.return_value = True
        MultipathClaim.unclaim_specific_hardware(self.VENDOR_ID, self.PRODUCT_ID)
        self.assertEqual(' '.join(execute.call_args[0][0]),
                         ("-n -u -d %s" % self.HARDWARE_ID))

    @unittest.parameters.iterate("policy", [None, "Fail Over Only", "Round Robin",
                                            "Least Queue Depth", "Least Blocks"])
    def test_extract_load_balancing(self, policy):
        from . import CLEAR_POLICY, ROUND_ROBIN, FAIL_OVER_ONLY, LEAST_BLOCKS, LEAST_QUEUE_DEPTH
        if policy:
            output = "\n".join(["", "MSDSM-wide Load Balance Policy: %s" % policy , ""])
        else:
            output = "\n".join(["", "No MSDSM-wide default load balance policy has been set", ""])
        self.assertIn(MultipathClaim._extract_load_balancing_from_output(output),
                      [CLEAR_POLICY, ROUND_ROBIN, FAIL_OVER_ONLY, LEAST_BLOCKS, LEAST_QUEUE_DEPTH])

    @unittest.parameters.iterate("policy", [None, "RR", "FOO", "LQD", "LB"])
    @unittest.parameters.iterate("is_output_empty", [False, True])
    def test_extract_hardware_specific_load_balancing(self, policy, is_output_empty):
        from . import CLEAR_POLICY, ROUND_ROBIN, FAIL_OVER_ONLY, LEAST_BLOCKS, LEAST_QUEUE_DEPTH
        if is_output_empty:
            output = "\n".join(["", "No target-level default load balance policies have been set.", ""])
        else:
            if policy is None:
                raise unittest.SkipTest
            output = "\n".join(["",
                                """"Target H/W Identifier   "   LB Policy                              """,
                                """-------------------------------------------------------------------------------""",
                                """"ABC     123             "   %s                                     """ % policy,
                                ""])
        if is_output_empty:
            self.assertEqual(MultipathClaim._extract_hardware_specific_load_balacing_policy(output, self.HARDWARE_ID),
                             CLEAR_POLICY)
        else:
            self.assertIn(MultipathClaim._extract_hardware_specific_load_balacing_policy(output, self.HARDWARE_ID),
                          [ROUND_ROBIN, FAIL_OVER_ONLY, LEAST_BLOCKS, LEAST_QUEUE_DEPTH])

    @mock.patch.object(MultipathClaim, "execute")
    def test_get_default_load_balancing_policy(self, execute):
        raise unittest.SkipTest
        from . import ROUND_ROBIN
        output = "\n".join(["", "MSDSM-wide Load Balance Policy: Round Robin", ""])
        execute.return_value = output
        self.assertEqual(MultipathClaim.get_default_load_balancing_policy(), ROUND_ROBIN)
        self.assertEqual(" ".join(execute.call_args[0][0]), "-s -m")

    @mock.patch.object(MultipathClaim, "execute")
    def test_set_default_load_balancing_policy(self, execute):
        raise unittest.SkipTest
        from . import ROUND_ROBIN
        MultipathClaim.set_default_load_balancing_policy(ROUND_ROBIN)
        self.assertEqual(" ".join(execute.call_args[0][0]), "-l -m %s" % ROUND_ROBIN)

    @mock.patch.object(MultipathClaim, "execute")
    def test_get_hardware_specific_load_balancing_policy(self, execute):
        raise unittest.SkipTest
        from . import ROUND_ROBIN
        output = "\n".join(["",
                            """"Target H/W Identifier   "   LB Policy                              """,
                            """-------------------------------------------------------------------------------""",
                            """"ABC     123             "   RR                                     """,
                            ""])
        execute.return_value = output
        args = (self.VENDOR_ID, self.PRODUCT_ID)
        self.assertEqual(MultipathClaim.get_hardware_specific_load_balancing_poicy(*args), ROUND_ROBIN)
        self.assertEqual(" ".join(execute.call_args[0][0]), "-s -t")

    @mock.patch.object(MultipathClaim, "execute")
    def test_set_hardware_specific_load_balancing_policy(self, execute):
        raise unittest.SkipTest
        from . import ROUND_ROBIN
        MultipathClaim.set_hardware_specific_load_balancing_policy(self.VENDOR_ID, self.PRODUCT_ID, ROUND_ROBIN)
        self.assertEqual(" ".join(execute.call_args[0][0]), "-l -t %s %s" % (self.HARDWARE_ID, ROUND_ROBIN))

    def _get_sample_device_and_policy(self):
        from ..wmi.model import Device, PdoInformation, LoadBalancePolicy, DSM_Path
        from . import FAIL_OVER_ONLY
        device = Device(None)
        paths = [PdoInformation(None), PdoInformation(None)]
        paths[0]._values['PathIdentifier'] = 1996685312
        paths[0].DeviceState = 0
        paths[1]._values['PathIdentifier'] = 1996685313
        paths[1].DeviceState = 1
        device._PdoInformation = paths
        device._values["DeviceName"] = r"\Device\MPIODisk123"
        device._values["InstanceName"] = "something"

        policy = LoadBalancePolicy(None, device.InstanceName)
        dsm_paths = [DSM_Path(None), DSM_Path(None)]
        dsm_paths[0]._values['DsmPathId'] = 1996685312
        dsm_paths[0].PathWeight = 0
        dsm_paths[0].PreferredPath = 1
        dsm_paths[1]._values['DsmPathId'] = 1996685313
        dsm_paths[1].PathWeight = 0
        dsm_paths[1].PreferredPath = 0
        policy._DSM_Paths = dsm_paths
        policy.LoadBalancePolicy = FAIL_OVER_ONLY

        return device, policy

    @mock.patch.object(MultipathClaim, "execute")
    def test_set_device_specific_load_balancing_policy__simple(self, execute):
        raise unittest.SkipTest
        from . import ROUND_ROBIN
        device, policy = self._get_sample_device_and_policy()
        policy.LoadBalancePolicy = ROUND_ROBIN
        MultipathClaim.set_device_specific_load_balancing_policy(device, policy)
        call_args = execute.call_args[0][0]
        self.assertEqual(" ".join(call_args),
                         "-l -d 123 2")

    @mock.patch.object(MultipathClaim, "execute")
    def test_set_device_specific_load_balancing_policy__complex(self, execute):
        raise unittest.SkipTest
        from . import ROUND_ROBIN
        device, policy = self._get_sample_device_and_policy()
        MultipathClaim.set_device_specific_load_balancing_policy(device, policy)
        call_args = execute.call_args[0][0]
        self.assertEqual(call_args, "-l -d 123 1 0000000077030000 0 0 1 0000000077030001 1 0 0".split())

    @mock.patch("infi.registry.LocalComputer")
    def test_get_claimed_hardware(self, LocalComputer):
        class Mock(object):
            class SubMock(object):
                @classmethod
                def to_python_object(cls):
                    return [self.HARDWARE_ID]
            values_store = dict(MPIOSupportedDeviceList=SubMock())
        mock = Mock()
        LocalComputer.return_value.local_machine = \
            {"SYSTEM\\CurrentControlSet\\Control\\MPDEV":mock}
        MultipathClaim.get_claimed_hardware()

    @unittest.parameters.iterate("new_policy", [CLEAR_POLICY, FAIL_OVER_ONLY, ROUND_ROBIN, ROUND_ROBIN_WITH_SUBSET,
                                            LEAST_QUEUE_DEPTH, WEIGHTED_PATHS, LEAST_BLOCKS])
    def test_change_load_balancing_policy(self, new_policy):
        raise unittest.SkipTest
        from ..wmi import WmiClient, get_multipath_devices, get_load_balace_policies
        client = WmiClient()
        devices = get_multipath_devices(client)
        policies = get_load_balace_policies(client)
        key = list(devices.keys())[0]
        device, policy = devices[key], policies[key]
        policy.LoadBalancePolicy = new_policy
        if new_policy == FAIL_OVER_ONLY or new_policy == ROUND_ROBIN_WITH_SUBSET:
            for path in [path for path in device.PdoInformation][0:1]:
                path.DeviceState = ACTIVE_OPTIMIZED
            for path in [path for path in device.PdoInformation][1:]:
                path.DeviceState = ACTIVE_NON_OPTIMIZED
        if new_policy == WEIGHTED_PATHS:
            for path in device.PdoInformation:
                path.DeviceState = ACTIVE_OPTIMIZED
            for path in policy.DSM_Paths:
                path.PathWeight = 1
        MultipathClaim.set_device_specific_load_balancing_policy(device, policy)

    def test_real_add_claim_rule(self):
        raise unittest.SkipTest
        MultipathClaim.claim_specific_hardware("A", "B")
        self.assertTrue(MultipathClaim.is_hardware_claimed("A", "B"))

