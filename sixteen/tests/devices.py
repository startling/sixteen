# -*- coding: utf-8 -*-

import unittest
from math import sqrt
from sixteen.dcpu16 import DCPU16
from sixteen.devices import Hardware
from sixteen.tests.dcpu16 import BaseDCPU16Test


class TestDevice(Hardware):
    identifier = 0xdeaddead
    manufacturer = 0xbeefbeef

    def __init__(self):
        self._next = False

    def on_interrupt(self, registers, ram):
        # square a and store it in b; overflow goes in EX
        overflow, result = divmod(registers["A"] ** 2, 0x10000)
        registers["B"] = result
        registers["EX"] = overflow

    def interrupt_next(self):
        "A function to tell this device to interrupt on the next turn."
        self._next = True

    def on_cycle(self):
        # if we've told it to raise an interrupt...
        if self._next:
            self._next = False
            return 0xdead


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
            0x7e40, 0,
            # set a, 0xf0f0 to make sure we can continue after a hwi
            0x7c01, 0xf0f0,
        ])
        self.assertRegister("B", 4)
        self.assertRegister("EX", 0)
        self.assertRegister("A", 0xf0f0)

    def test_interrupts(self):
        self.cpu.ram[:5] = [
            # ias, :handler
            0x7d40, 0x0003,
            # sub pc, 1
            0x8b83, 
            # handler: set pc, 0xff0f
            0x7f81, 0xff0f
        ]
        # cycle 3 times
        self.cpu.cycle()
        self.cpu.cycle()
        self.cpu.cycle()
        # make the device interrupt
        self.device.interrupt_next()
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure we got a message.
        self.assertRegister("A", 0xdead)

    def test_multiple_interrupts(self):
        self.cpu.ram[:5] = [
            # ias, :handler
            0x7d40, 0x0003,
            # sub pc, 1
            0x8b83,
            # handler: add b, 80 / rfi 0
            0x7c22, 0x0050, 0x8560
        ]
        # cycle 3 times
        self.cpu.cycle()
        self.cpu.cycle()
        self.cpu.cycle()
        # make the device interrupt
        self.device.interrupt_next()
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure we got a message.
        self.assertRegister("A", 0xdead)
        self.assertRegister("B", 80)
        self.cpu.cycle()
        # make the device interrupt again
        self.device.interrupt_next()
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertRegister("B", 160)
