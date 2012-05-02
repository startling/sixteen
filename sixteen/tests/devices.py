# -*- coding: utf-8 -*-

import unittest
from math import sqrt
from sixteen.dcpu16 import DCPU16
from sixteen.devices import Hardware
from sixteen.tests.dcpu16 import BaseDCPU16Test


class TestDevice(Hardware):
    identifier = 0xdeaddead
    manufacturer = 0xbeefbeef

    def on_interrupt(self, registers, ram):
        # square a and store it in b; overflow goes in EX
        overflow, result = divmod(registers["A"] ** 2, 0x10000)
        registers["B"] = result
        registers["EX"] = overflow


class DeviceTest(BaseDCPU16Test):
    def setUp(self):
        self.device = TestDevice()
        self.cpu = DCPU16([self.device])



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
        self.assertEqual(self.device.identifier, identifier)
        manufacturer = self.cpu.registers["X"] + (self.cpu.registers["Y"]
                << 16)
        self.assertEqual(self.device.manufacturer, manufacturer)

    def test_hwi(self):
        self.run_instructions([
            # set a, 2
            0x7c01, 2,
            # hwi 0
            0x7e40, 0
        ])
        self.assertRegister("B", 4)
        self.assertRegister("EX", 0)
