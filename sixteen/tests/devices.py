# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16
from sixteen.devices import Hardware
from sixteen.tests.dcpu16 import BaseDCPU16Test


class TestDevice(Hardware):
    identifier = 0xdeaddead
    manufacturer = 0xbeefbeef


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

    def test_hwq(self):
        self.run_instructions([
            # hwq 1
            0x7e20, 0
        ])
        identifier = self.cpu.registers["A"] + (self.cpu.registers["B"] << 16)
        self.assertEqual(TestDevice.identifier, identifier)
        manufacturer = self.cpu.registers["X"] + (self.cpu.registers["Y"]
                << 16)
        self.assertEqual(TestDevice.manufacturer, manufacturer)
