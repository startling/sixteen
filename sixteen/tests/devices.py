# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16
from sixteen.devices import Hardware
from sixteen.tests.dcpu16 import BaseDCPU16Test


class TestDevice(Hardware):
    pass


class DeviceTest(BaseDCPU16Test):
    def setUp(self):
        self.cpu = DCPU16([TestDevice()])



class TestDeviceOperations(DeviceTest, unittest.TestCase):
    def test_hwn(self):
        self.run_instructions([
            # hwn, A
            0x0200
        ])
        self.assertRegister("A", 1)
