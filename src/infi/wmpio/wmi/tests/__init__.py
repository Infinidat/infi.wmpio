
from contextlib import contextmanager, nested
from time import clock
from ...scripts import walk
from infi import unittest
from infi.execute import execute
from os.path import abspath, dirname, exists, join

import mock
from infi.wmpio.wmi import WmiClient

WALK_VBS = abspath(join(dirname(__file__), 'walk.vbs'))

class TestCase(unittest.TestCase):
    @contextmanager
    def assertTakesLess(self, secs):
        start = clock()
        yield
        end = clock()
        self.assertLess(end - start, secs)

class ExeuctionTestCase(TestCase):
    def setUp(self):
        from os import name
        if name != 'nt':
            raise unittest.SkipTest

    @unittest.parameters.iterate("read_all", [True, False])
    @unittest.parameters.iterate("subtree", [True, False])
    def test_walk(self, read_all, subtree):
        walk(10, subtree, read_all)

class PerformanceTestCase(TestCase):
    def setUp(self):
        from os import name
        if name != 'nt':
            raise unittest.SkipTest

    def _time_vbscript(self, subtree, read_all):
        assert exists(WALK_VBS)
        start = clock()
        vbs = execute(['cscript', WALK_VBS] + ['2000', '1' if subtree else '0',
                                               '1' if read_all else '0'])
        vbs.wait()
        assert vbs.get_returncode() == 0
        end = clock()
        return end - start

    @unittest.parameters.iterate("read_all", [True, False])
    @unittest.parameters.iterate("subtree", [True, False])
    def test_faster_than_vbscript(self, subtree, read_all):
        with self.assertTakesLess(self._time_vbscript(subtree, read_all) + 5):
            walk(2000, subtree, read_all)