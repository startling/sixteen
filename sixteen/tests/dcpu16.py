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

    def assert_register(self, name, value):
        self.assertEquals(self.cpu.registers[name], value)

    def assert_RAM(self, addr, value):
        self.assertEquals(self.cpu.ram[addr], value)
