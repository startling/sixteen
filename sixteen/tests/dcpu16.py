# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16


class TestDCPU16(unittest.TestCase):
    def setUp(self):
        self.cpu = DCPU16()

    def test_set_next_word(self):
        # set A to the next word.
        self.cpu[0] = 0x7c01
        # set the next word to 0x0030 / 48
        self.cpu[1] = 0x0030
        # run for a cycle
        self.cpu.cycle()
        # and then assert that the register was assigned to.
        self.assertEquals(self.cpu.registers["A"], 0x0030)

    def test_set_short_literal(self):
        # set I to 10.
        self.cpu[0] = 0xa861
        # run for a cycle
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["I"], 0x000a)

    def test_multiple_instructions(self):
        # set X, 0x04
        self.cpu[0] = 0x9031
        # set A, 001a
        self.cpu[1] = 0x7c01
        self.cpu[2] = 0x001a
        # run...
        self.cpu.cycle()
        self.cpu.cycle()
        # and then check things
        self.assertEquals(self.cpu.registers["X"], 0x0004)
        self.assertEquals(self.cpu.registers["A"], 0x001a)

    def test_set_register_pointer(self):
        # set A, 0x0020 
        self.cpu[0] = 0x7c01
        self.cpu[1] = 0x0020
        # set the address A points to to be 0xbeef
        self.cpu[2] = 0x7c81
        self.cpu[3] = 0xbeef
        # run
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure we made the address 0x0020 be 0xbeef
        self.assertEquals(self.cpu[0x0020], 0xbeef)
