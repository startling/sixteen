# -*- coding: utf-8 -*-

import unittest
from sixteen.words import Word


# a bunch of instructions, seperated into their components
instructions = {
    # word -> opcode, a, b
    # set A to the next word
    "7c01": (0x01, 0x00, 0x1f),
    # ifn A, 0x10 (short form, 0x30) 
    "c00d": (0x0d, 0x00, 0x30),
    # set I to 10 (short form, 0x2a)
    "a861": (0x01, 0x06, 0x2a),
    # shl x, 4 (short form 0x24)
    "9037": (0x07, 0x03, 0x24),
}


class TestWords(unittest.TestCase):
    def test_instructions(self):
        for code, (eo, ea, eb) in instructions.items():
            o, a, b = Word.from_hex(code).as_opcode()
            #print "expected: %x %x %x" % (eo, ea, eb)
            #print "got     : %x %x %x" % (o, a, b)
            self.assertEqual((eo, ea, eb), (o, a, b))
