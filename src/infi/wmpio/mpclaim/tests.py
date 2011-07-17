import unittest
import mock

class MpclaimTestCase(unittest.TestCase):
    @mock.patch("infi.wmpio.mpclaim.MultipathClaim.get_claimed_devices")
    def test_is_device_claimed(self, get_claimed_devices):
        from . import MultipathClaim
        get_claimed_devices.return_value = [dict(vendor_id="foo", product_id="bar"),
                                            dict(vendor_id="hello", product_id="world"), ]
        self.assertTrue(MultipathClaim.is_device_claimed("hello", "world"))
        self.assertTrue(MultipathClaim.is_device_claimed("foo", "bar"))

