# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16


class BaseDCPU16Test(object):
    def setUp(self):
        self.cpu = DCPU16()

    def run_instructions(self, words):
        self.cpu.ram[:len(words)] = list(words)
        count = 0
        while count < len(words):
            consumed = self.cpu.cycle()
            count += len(consumed)

    def assertRegister(self, name, value):
        self.assertEquals(self.cpu.registers[name], value)

    def assertRAM(self, addr, value):
        self.assertEquals(self.cpu.ram[addr], value)


class TestSet(BaseDCPU16Test, unittest.TestCase):
    def test_set_ram_pointer(self):
        self.run_instructions([
            # set ram addres 0x1337 to 0xbeef
            0x7be1, 0x1337, 0xbeef
        ])
        self.assertRAM(0x1337, 0xbeef)


class TestAdd(BaseDCPU16Test, unittest.TestCase):
    def test_add_pointer_literal(self):
        self.run_instructions([
            # set ram addres 0x1337 to 0xbeef
            0x7be1, 0x1337, 0xbeef,
            # add 0x1000 to 0xbeef
            0x7be2, 0x1337, 0x1000
        ])
        self.assertRAM(0x1337, 0xbeef + 0x1000)
