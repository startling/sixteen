# -*- coding: utf-8 -*-

import unittest
from sixteen.words import as_opcode, from_opcode


# a bunch of instructions, seperated into their components
instructions = {
    # word -> opcode, a, b
    # set A to the next word
    0x7c01: (0x01, 0x00, 0x1f),
    # ifn A, 0x10 (short form, 0x30) 
    0xc00d: (0x0d, 0x00, 0x30),
    # set I to 10 (short form, 0x2a)
    0xa861: (0x01, 0x06, 0x2a),
    # shl x, 4 (short form 0x24)
    0x9037: (0x07, 0x03, 0x24),
}


class TestWords(unittest.TestCase):
    def test_from_opcode(self):
        for code, (eo, ea, eb) in instructions.items():
            self.assertEquals(from_opcode(eo, ea, eb), code)

    def test_instructions(self):
        for code, (eo, ea, eb) in instructions.items():
            o, a, b = as_opcode(code)
            #print "expected: %x %x %x" % (eo, ea, eb)
            #print "got     : %x %x %x" % (o, a, b)
            self.assertEqual((eo, ea, eb), (o, a, b))
