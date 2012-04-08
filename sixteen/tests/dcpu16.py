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

    def test_set_next_word_pointer(self):
        self.cpu[:3] = [
            # set memory address 0x1000 to 0x0020
            0x7de1, 0x1000, 0x0020
        ]
        self.cpu.cycle()
        self.assertEquals(self.cpu[0x1000], 0x0020)


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

    def test_pop_push_peek(self):
        self.cpu[:3] = [
            # push 0x0001 (short form 0x21)
            0x85a1,
            # set A to whatever's peeked (should be 0x0001)
            0x6401,
            # set B to whatever's peeked (also should be 0x0001)
            0x6411,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0x0001)
        self.assertEquals(self.cpu.registers["B"], 0x0001)

    def test_add(self):
        self.cpu[:3] = [
            # set A to 0x0001 (short form 0x21)
            0x8401, 
            # and then add two (short form 0x22) to it
            0x8802,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0x0003)
        # and make sure the overflow is empty
        self.assertEquals(self.cpu.registers["O"], 0x0000)

    def test_add_overflow(self):
        self.cpu[:4] = [
            # set A to 0x0005
            0x7c01, 0x0005,
            # and then add 0xffff 
            0x7c02, 0xffff
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure the overflow is 0x0001
        self.assertEquals(self.cpu.registers["O"], 0x0001)
        # and that A is 0x0004
        self.assertEquals(self.cpu.registers["A"], 0x0004)
    
    def test_sub(self):
        self.cpu[:4] = [
            # set A to 0x0005
            0x7c01, 0xffff,
            # and then subtract 0xffff 
            0x7c03, 0x0005,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure the underflow is empty
        self.assertEquals(self.cpu.registers["O"], 0x0000)
        # and that A is 0xfffa
        self.assertEquals(self.cpu.registers["A"], 0xfffa)

    def test_sub_underflow(self):
        self.cpu[:4] = [
            # set A to 0x0005
            0x7c01, 0x0005,
            # and then subtract 0xffff 
            0x7c03, 0xffff
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure the underflow is 0xffff
        self.assertEquals(self.cpu.registers["O"], 0xffff)
        # and that A is 0x0006.
        self.assertEquals(self.cpu.registers["A"], 0x0006)

    def test_mul(self):
        self.cpu[:4] = [
            # set A to 0x0008
            0x7c01, 0x0008,
            # and then multiply two
            0x7c04, 0x0002,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0x0010)
        # and make sure the overflow is empty
        self.assertEquals(self.cpu.registers["O"], 0x0000)

    def test_mul_overflow(self):
        self.cpu[:4] = [
            # set A to 0xffff
            0x7c01, 0xffff,
            # and then multiply 0xffff
            0x7c04, 0xffff,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0x0001)
        # and make sure the overflow is correct
        self.assertEquals(self.cpu.registers["O"], 0xfffe)
        # I think I did the math right?

    def test_div(self):
        self.cpu[:4] = [
            # set A to 0x0008
            0x7c01, 0x0008,
            # and then divide by four
            0x7c05, 0x0004,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0x0002)
        # and make sure the overflow is empty
        self.assertEquals(self.cpu.registers["O"], 0x0000)

    def test_div_overflow(self):
        self.cpu[:4] = [
            # set A to 0x0009
            0x7c01, 0x0009,
            # and then divide by 0x0007
            0x7c05, 0x0007,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0x0001)
        # and make sure the overflow is 0x4924
        self.assertEquals(self.cpu.registers["O"], 0x4924)

    def test_div_by_zero(self):
        self.cpu[:4] = [
            # set A to 0x0008
            0x7c01, 0x0008,
            # and then divide by zero
            0x7c05, 0x0000,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure divide-by-zero sets A to 0
        self.assertEquals(self.cpu.registers["A"], 0x0000)
        # and make sure the overflow is empty
        self.assertEquals(self.cpu.registers["O"], 0x0000)

    def test_AND(self):
        self.cpu[:4] = [
            # set A 
            0x7c01, 0b1000000000000000,
            # and then AND
            0x7c09, 0b1111111111111111,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0b1000000000000000)

    def test_BOR(self):
        self.cpu[:4] = [
            # set A 
            0x7c01, 0b1000000000000000,
            # and then BOR
            0x7c0a, 0b1111111111111111,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0b1111111111111111)

    def test_XOR(self):
        self.cpu[:4] = [
            # set A 
            0x7c01, 0b1000000000000000,
            # and then XOR
            0x7c0b, 0b1111111111111111,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0b0111111111111111)

    def test_IFE(self):
        self.cpu[:4] = [
            # if A equals 0x0000 (it should), set A to 0xbeef
            0x7c0c, 0x0000, 0x7c01, 0xbeef,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0xbeef)

    def test_IFN(self):
        self.cpu[:6] = [
            # if A doesn't equal 0x0001 (it doesn't), set A to 0xbeef
            0x7c0d, 0x0001, 0x7c01, 0xbeef,
            # otherwise, set it to 0xdecaf
            0x7c01, 0xdecaf
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0xbeef)

    def test_IFG(self):
        self.cpu[:4] = [
            # if A > 0x0000 (it shouldn't), set A to 0xbeef
            0x7c0e, 0x0000, 0x7c01, 0xbeef,
            # otherwise set it to 0xdecaf
            0x7c01, 0xdecaf
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0xdecaf)

    def test_IFB(self):
        self.cpu[:4] = [
            # if A & 0x0000 != 1 (false), set A to 0xbeef
            0x7c0f, 0x0001, 0x7c01, 0xbeef,
            # otherwise set it to 0xdecaf
            0x7c01, 0xdecaf
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0xdecaf)


    def test_mod(self):
        self.cpu[:4] = [
            # set A to 0x000c
            0x7c01, 0x000c,
            # and then MOD by four
            0x7c06, 0x0005,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        # make sure it's 2 (1
        self.assertEquals(self.cpu.registers["A"], 0x0002)

    def test_shl(self):
        self.cpu[:4] = [
            # set A to 0x0001
            0x7c01, 0b0000000000000001,
            # and then shift left by four
            0x7c07, 0x0004,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0b0000000000010000)
        # and make sure the overflow is 
        self.assertEquals(self.cpu.registers["O"], 0x0000)

    def test_shl_overflow(self):
        self.cpu[:4] = [
            # set A to 0x0001
            0x7c01, 0b1111000000000001,
            # and then shift left by four
            0x7c07, 0x0004,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0b0000000000010000)
        # and make sure the overflow is right.
        self.assertEquals(self.cpu.registers["O"], 0b0000000000001111)

    def test_shr(self):
        self.cpu[:4] = [
            # set A to 0x0001
            0x7c01, 0b0000000000010000,
            # and then shift right by four
            0x7c08, 0x0004,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0b0000000000000001)
        # and make sure the overflow is 
        self.assertEquals(self.cpu.registers["O"], 0x0000)

    def test_shr_overflow(self):
        self.cpu[:4] = [
            # set A to 0x0001
            0x7c01, 0b1000000000001111,
            # and then shift right by four
            0x7c08, 0x0004,
        ]
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0b0000100000000000)
        # and make sure the overflow is right.
        self.assertEquals(self.cpu.registers["O"], 0b1111000000000000)

    def test_jsr(self):
        self.cpu[:6] = [
            # JSR 0x0004
            0x7c10, 0x0004,
            # blank junk to jump over
            0x0000, 0x0000,
            # set A to 0xbeef
            0x7c01, 0xbeef,
            # SET PC, POP, e.g. go to after the JSR
            0x61c1
        ]
        # make sure JSR jumps to 0x0004
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["PC"], 0x0004)
        # make sure A gets set
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["A"], 0xbeef)
        # make sure the PC goes back to 0x0002
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["PC"], 0x0002)

    def test_pc_overflow(self):
        self.cpu[:3] = [
            # add 2 to A
            0x8802, 
            # set PC, 0xffff
            0x7dc1, 0xffff
        ]
        # SET PC, PC -- a no-op.
        self.cpu.RAM[0xffff] = 0x71c1
        self.cpu
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEquals(self.cpu.registers["PC"], 0xffff)
        self.cpu.cycle()
        self.cpu.cycle()
        self.assertEqual(self.cpu.registers["A"], 0x0004)
