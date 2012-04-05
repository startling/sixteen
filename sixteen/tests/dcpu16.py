# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16


class TestDCPU16(unittest.TestCase):
    def setUp(self):
        self.cpu = DCPU16()

    def test_set_next_word(self):
        # set A to the next word.
        self.cpu[0] = "7c01"
        # set the next word to 0x0030 / 48
        self.cpu[1] = "0030"
        # run for a cycle
        self.cpu.cycle()
        # and then assert that the register was assigned to.
        self.assertEquals(self.cpu.registers["A"], 0x0030)

    def test_set_short_literal(self):
        # set I to 10.
        self.cpu[0] = "a861"
        # run for a cycle
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["I"], 0x000a)

    def test_multiple_instructions(self):
        # set X, 0x04
        self.cpu[0] = "9031"
        # set A, 001a
        self.cpu[1] = "7c01"
        self.cpu[2] = "001a"
        # run...
        self.cpu.cycle()
        self.cpu.cycle()
        # and then check things
        self.assertEquals(self.cpu.registers["X"], 0x0004)
        self.assertEquals(self.cpu.registers["A"], 0x001a)
