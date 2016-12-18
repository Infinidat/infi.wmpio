from __future__ import print_function

from contextlib import contextmanager
from time import clock
from ...scripts import walk
from infi import unittest
from infi.execute import execute
from os.path import abspath, dirname, exists, join

import mock
import logging

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
        raise unittest.SkipTest

    def _time_vbscript(self, subtree, read_all):
        assert exists(WALK_VBS)
        start = clock()
        vbs = execute(['cscript', WALK_VBS] + ['2000', '1' if subtree else '0',
                                               '1' if read_all else '0'])
        end = clock()
        print(vbs.get_stdout())
        print(vbs.get_stderr())
        self.assertEqual(vbs.get_returncode(), 0)
        output = vbs.get_stderr() + vbs.get_stdout()
        self.assertFalse(WALK_VBS in output, 'cscript returned an error')
        return end - start

    @unittest.parameters.iterate("count", [100, 500, 1000])
    @unittest.parameters.iterate("read_all", [True, False])
    @unittest.parameters.iterate("subtree", [True, False])
    def test_faster_than_vbscript(self, subtree, read_all, count):
        logging.debug("running walk with count=%s, subtree=%s, read_all=%s",
                      count, subtree, read_all)
        vbscript_time = self._time_vbscript(subtree, read_all)
        with self.assertTakesLess(vbscript_time*110/100):
            walk(count, subtree, read_all)
