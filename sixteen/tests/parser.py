# -*- coding: utf-8 -*-

import unittest
from sixteen.parser import AssemblyParser
from itertools import chain


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = AssemblyParser()
        self.parse = self.parser.parse

    def assertParses(self, given, expected):
        self.assertEquals(self.parse(given), expected)

    def test_parse_registers(self):
        self.assertParses("A", (0x00, None))
        self.assertParses("B", (0x01, None))
        self.assertParses("Y", (0x04, None))
        self.assertParses("J", (0x07, None))

    def test_parse_register_pointers(self):
        self.assertParses("[A]", (0x08, None))
        self.assertParses("[B]", (0x09, None))
        self.assertParses("[Y]", (0x0c, None))
        self.assertParses("[J]", (0x0f, None))

    def test_parse_next_word_plus_registers(self):
        self.assertParses("[0x0000 + A]", (0x10, 0x0000)) 
        self.assertParses("[0x0300 + B]", (0x11, 0x0300)) 
        self.assertParses("[0xffff + I]", (0x16, 0xffff)) 
        self.assertParses("[0x03f0 + J]", (0x17, 0x03f0)) 

    def test_parse_POP(self):
        self.assertParses("POP", (0x18, None))
        self.assertParses("[SP++]", (0x18, None))

    def test_parse_POP(self):
        self.assertParses("PEEK", (0x19, None))
        self.assertParses("[SP]", (0x19, None))

    def test_parse_PUSH(self):
        self.assertParses("PUSH", (0x1a, None))
        self.assertParses("[--SP]", (0x1a, None))

    def test_parse_SP(self):
        self.assertParses("SP", (0x1b, None))

    def test_parse_PC(self):
        self.assertParses("PC", (0x1c, None))

    def test_parse_O(self):
        self.assertParses("O", (0x1d, None))

    def test_parse_next_word_pointer(self):
        self.assertParses("[0x0000]", (0x1e, 0x0000)) 
        self.assertParses("[0x0300]", (0x1e, 0x0300)) 
        self.assertParses("[0xffff]", (0x1e, 0xffff)) 
        self.assertParses("[0x03f0]", (0x1e, 0x03f0)) 

    def test_parse_SET(self):
        self.assertParses("SET", 0x1)

    def test_parse_ADD(self):
        self.assertParses("ADD", 0x2)

    def test_parse_SUB(self):
        self.assertParses("SUB", 0x3)

    def test_parse_MUL(self):
        self.assertParses("MUL", 0x4)

    def test_parse_DIV(self):
        self.assertParses("DIV", 0x5)

    def test_parse_MOD(self):
        self.assertParses("MOD", 0x6)

    def test_parse_SHL(self):
        self.assertParses("SHL", 0x7)

    def test_parse_SHR(self):
        self.assertParses("SHR", 0x8)

    def test_parse_AND(self):
        self.assertParses("AND", 0x9)

    def test_parse_BOR(self):
        self.assertParses("BOR", 0xa)

    def test_parse_XOR(self):
        self.assertParses("XOR", 0xb)

    def test_parse_IFE(self):
        self.assertParses("IFE", 0xc)

    def test_parse_IFN(self):
        self.assertParses("IFN", 0xd)

    def test_parse_IFG(self):
        self.assertParses("IFG", 0xe)

    def test_parse_IFB(self):
        self.assertParses("IFB", 0xf)

    def test_instruction(self):
        self.assertParses("SET A, 0x30", (0x1, 0x0, 0x1f, 0x30, None))
        self.assertParses("SET A 0x30", (0x1, 0x0, 0x1f, 0x30, None))
        self.assertParses("SET I, 10", (0x1, 0x06, 0x2a, None, None))
        self.assertParses("SUB A, [0x1000]", (0x3, 0x0, 0x1e, 0x1000, None))
        self.assertParses("IFN A, 0x10", (0xd, 0x0, 0x30, None, None))

    def test_comments(self):
        self.assertParses("SET I, 10; comment", (0x1, 0x06, 0x2a, None, None))
        self.assertParses("SET I, 10;comment", (0x1, 0x06, 0x2a, None, None))
        self.assertParses("SET I, 10 ;comment", (0x1, 0x06, 0x2a, None, None))
        self.assertParses("SET I, 10 ; comment", (0x1, 0x06, 0x2a, None, None))

    def test_ignores(self):
        self.assertParses(" SET A, 0x30   ", (0x1, 0x0, 0x1f, 0x30, None))
        self.assertParses("\t SET I, 10 ; hi", (0x1, 0x06, 0x2a, None, None))
        self.assertParses("; hi comment", (None,))
        self.assertParses("    ;comment", (None,))
        self.assertParses("\t      ", (None,))

    def test_long_literals(self):
        self.assertParses("0x30", (0x1f, 0x30))
        self.assertParses("0b1111111", (0x1f, 127))
        self.assertParses("317", (0x1f, 317))

    def test_short_literals(self):
        self.assertParses("0", (0x20, None))
        self.assertParses("0x1f", (0x3f, None))
        self.assertParses("0b11", (0x23, None))

    def test_to_ints(self):
        assembly = """
                SET A, 0x30        ; 
                SET [0x1000], 0x20 ; wooh , comment
                SUB A, [0x1000]
                IFN A, 0x10
        """
        ints = (self.parser.parse_to_ints(l) for l in assembly.split("\n"))
        flattened = chain(*ints)
        self.assertEqual(list(flattened), [0x7c01, 0x0030, 0x7de1, 0x1000,
            0x0020, 0x7803, 0x1000, 0xc00d])

    def test_labels(self):
        self.assertParses("SET PC, :label", (0x1, 0x1c, 0x1f, ":label", None))
        self.assertParses("SET A, :label", (0x1, 0x00, 0x1f, ":label", None))

