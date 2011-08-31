
from contextlib import nested
from infi import unittest

import mock
from . import WmiClient, WmiObject

class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self._raise_if_should()

    def _raise_if_should(self):
        from os import name
        if name != 'nt':
            raise unittest.SkipTest

    def test_client(self):
        client = WmiClient()

    def test_execute_query(self):
        from .. import DEVICES_QUERY
        client = WmiClient()
        results = [item for item in client.execute_query(DEVICES_QUERY)]
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

class MockClientTestCase(ClientTestCase):
    def _raise_if_should(self):
        pass

    def test_client(self):
        with nested(mock.patch("infi.wmpio.wmi.interface.get_comtypes_client")) as (client,):
            ClientTestCase.test_client(self)

    def test_execute_query(self):
        with nested(mock.patch("infi.wmpio.wmi.interface.get_comtypes_client")) as (client,):
            class ResultSet(object):
                Count = 3
                def ItemIndex(self, index):
                    return None
            client.return_value.ExecQuery.return_value = ResultSet()
            ClientTestCase.test_execute_query(self)
            client.ExecQuery.return_value.ItemIndex.return_value = None


class Property(object):
    def __init__(self, value):
        super(Property, self).__init__()
        self.call_count = 0
        self.value = value

    @property
    def Value(self):
        self.call_count += 1
        return self.value

class ComObject(object):
    def __init__(self, value):
        super(ComObject, self).__init__()
        self.call_count = dict()
        self.call_count['Properties_'] = 0
        self.call_count['Item'] = 0
        self.property = Property(value)

    @property
    def Properties_(self):
        self.call_count['Properties_'] += 1
        return self

    def Item(self, attr):
        self.call_count['Item'] += 1
        return self.property

class WmiObjectTestCase(unittest.TestCase):
    def test_get_attribute__once(self):
        obj = WmiObject(ComObject('attr'))
        value = obj.get_wmi_attribute('attr')
        self.assertEqual(value, 'attr')

    def test_get_attribute__multiple_times(self):
        com = ComObject('attr')
        obj = WmiObject(com)
        [obj.get_wmi_attribute('attr') for _ in range(1024)]
        self.assertEqual(com.call_count['Properties_'], 1)
        self.assertEqual(com.call_count['Item'], 1)
        self.assertEqual(com.call_count['Properties_'], 1)
        self.assertEqual(com.property.call_count, 1)
