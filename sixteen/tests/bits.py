# -*- coding: utf-8 -*-

import unittest
from sixteen.bits import as_instruction, from_instruction, bit_iter


# a bunch of instructions, seperated into their components
instructions = {
    # word -> opcode, a, b
    # new words: aaaaaabbbbbooooo
    # that is, o ^ a << 10 ^ b << 5
    # set A to the next word
    0x7c01: (0x01, 0x00, 0x1f),
    # ifn A, pc (0x1c)
    0x7013: (0x13, 0x00, 0x1c),
    # set I to the next word as pointer (1e)
    0x78c1: (0x01, 0x06, 0x1e),
    # set a, 1 (short form 0x22)
    0x8801: (0x1, 0x0, 0x22)
}


class TestBits(unittest.TestCase):
    def test_from_instruction(self):
        for code, (eo, eb, ea) in instructions.items():
            self.assertEquals(from_instruction(eo, eb, ea), code)

    def test_instructions(self):
        for code, (eo, eb, ea) in instructions.items():
            o, b, a = as_instruction(code)
            #print "expected: %x %x %x" % (eo, ea, eb)
            #print "got     : %x %x %x" % (o, a, b)
            self.assertEqual((eo, eb, ea), (o, b, a))


class TestBitIter(unittest.TestCase):
    def assertBits(self, given, digits, expected):
        self.assertEquals(list(bit_iter(given, digits)), expected)

    def test_bit_iter(self):
        self.assertBits(0b0001, 4, [0, 0, 0, 1])
        self.assertBits(0b0111, 4, [0, 1, 1, 1])
        self.assertBits(0b1011, 4, [1, 0, 1, 1])
        self.assertBits(0b1000, 4, [1, 0, 0, 0])
        self.assertBits(0b10001000, 8, [1, 0, 0, 0, 1, 0, 0, 0])
