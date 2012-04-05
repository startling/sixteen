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

    def test_register_pointer(self):
        # set A, 0x0020 
        self.cpu[0] = 0x7c01
        self.cpu[1] = 0x0020
        # set the address A points to to be 0xbeef
        self.cpu[2] = 0x7c81
        self.cpu[3] = 0xbeef
        # save [A] as B
        self.cpu[4] = 0x2011
        # run
        self.cpu.cycle()
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure we made the address 0x0020 be 0xbeef
        self.assertEquals(self.cpu[0x0020], 0xbeef)
        self.assertEquals(self.cpu.registers["B"], 0xbeef)

    def test_register_plus_next(self):
        self.cpu[:4] = [
            # set A, 0x0000
            0x7c01, 0x0000,
            # set B to [A + next register (0x0001 in this case)]
            # the total should be 0x0002, which should be 0x4011
            0x4011, 0x0002,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["B"], 0x4011)

    def test_next_word_pointer(self):
        self.cpu[:3] = [
            # set A to the value where the next word points to.
            # hint: it points to address 2, which is 0xbeef
            0x7801, 0x0002, 0xbeef
        ]
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0xbeef)

    def test_get_set_pc(self):
        self.cpu[:4] = [
            # set the program counter to the next word
            0x7dc1, 0x0003,
            # blank word, that we'll jump over
            0x0000,
            # store the PC in A
            0x7001
        ]
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["PC"], 0x0003)
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["PC"], self.cpu.registers["A"])

    def test_pop_push(self):
        self.cpu[:2] = [
            # push 0x0001 (short form 0x21)
            0x85a1,
            # set A to whatever's popped (should be 0x0001)
            0x6001,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0x0001)
        # and the stack pointer should be 0x0000 again
        self.assertEquals(self.cpu.registers["SP"], 0x0000)
