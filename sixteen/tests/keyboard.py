# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16
from sixteen.devices import Keyboard
from sixteen.tests.dcpu16 import BaseDCPU16Test


class KeyboardTest(BaseDCPU16Test, unittest.TestCase):
    def setUp(self):
        self.device = Keyboard()
        self.cpu = DCPU16([self.device])

    def test_multiple_interrupts(self):
        self.cpu.ram[:5] = [
            # ias, :handler
            0x7d40, 0x0007,
            # turn on hardware interrupts with message "0xbeef"
            # set a, 3 / set b, 0xbeef / hwi, 0
            0x9001, 0x7c21, 0xbeef, 0x8640,
            # sub pc, 1
            0x8b83,
            # handler:
            # get the keypress from the device: set a, 1 / hwi, 0
            0x8801, 0x8640,
            # rfi 0
            0x8560
        ]
        # cycle 6 times
        for _ in xrange(6):
            self.cpu.cycle()
        # feed the keyboard "A"
        self.device.register_keypress(ord("A"))
        # cycle some more
        for _ in xrange(3):
            self.cpu.cycle()
        # make sure we got a message.
        self.assertRegister("C", ord("A"))
        # make the device interrupt again
        self.device.register_keypress(ord("B"))
        for _ in xrange(3):
            self.cpu.cycle()
        self.assertRegister("C", ord("B"))
