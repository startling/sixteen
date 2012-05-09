# -*- coding: utf-8 -*-

import unittest
from sixteen.assembler import ValueParser, AssemblyParser
from sixteen.words import from_opcode
from itertools import chain


class TestValues(unittest.TestCase):
    def setUp(self):
        self.parser = ValueParser()
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

    def test_parse_lowercase_registers(self):
        self.assertParses("a", (0x00, None))
        self.assertParses("b", (0x01, None))
        self.assertParses("y", (0x04, None))
        self.assertParses("j", (0x07, None))

    def test_parse_lowercase_register_pointers(self):
        self.assertParses("[a]", (0x08, None))
        self.assertParses("[b]", (0x09, None))
        self.assertParses("[y]", (0x0c, None))
        self.assertParses("[j]", (0x0f, None))

    def test_parse_lowercase_next_word_plus_registers(self):
        self.assertParses("[0x0000 + a]", (0x10, 0x0000)) 
        self.assertParses("[0x0300 + b]", (0x11, 0x0300)) 
        self.assertParses("[0xffff + i]", (0x16, 0xffff)) 
        self.assertParses("[0x03f0 + j]", (0x17, 0x03f0)) 
        self.assertParses("[0xffff + i]", (0x16, 0xffff)) 

    def test_parse_POP(self):
        self.assertParses("POP", (0x18, None))
        self.assertParses("[SP++]", (0x18, None))

    def test_parse_POP_lowercase(self):
        self.assertParses("pop", (0x18, None))
        self.assertParses("[sp++]", (0x18, None))

    def test_parse_PEEK(self):
        self.assertParses("PEEK", (0x19, None))
        self.assertParses("[SP]", (0x19, None))

    def test_parse_PEEK_lowercase(self):
        self.assertParses("peek", (0x19, None))
        self.assertParses("[sp]", (0x19, None))

    def test_parse_PUSH(self):
        self.assertParses("PUSH", (0x1a, None))
        self.assertParses("[--SP]", (0x1a, None))

    def test_parse_PUSH_lowercase(self):
        self.assertParses("push", (0x1a, None))
        self.assertParses("[--sp]", (0x1a, None))

    def test_parse_SP(self):
        self.assertParses("SP", (0x1b, None))

    def test_parse_SP_lowercase(self):
        self.assertParses("sp", (0x1b, None))

    def test_parse_PC(self):
        self.assertParses("PC", (0x1c, None))

    def test_parse_PC_lowercase(self):
        self.assertParses("pc", (0x1c, None))

    def test_parse_O(self):
        self.assertParses("O", (0x1d, None))

    def test_parse_O_lowercase(self):
        self.assertParses("o", (0x1d, None))

    def test_parse_next_word_pointer(self):
        self.assertParses("[0x0000]", (0x1e, 0x0000)) 
        self.assertParses("[0x0300]", (0x1e, 0x0300)) 
        self.assertParses("[0xffff]", (0x1e, 0xffff)) 
        self.assertParses("[0x03f0]", (0x1e, 0x03f0)) 

    def test_long_literals(self):
        self.assertParses("0x30", (0x1f, 0x30))
        self.assertParses("0b1111111", (0x1f, 127))
        self.assertParses("317", (0x1f, 317))

    def test_negative_literals(self):
        self.assertParses("-0x02", (0x1f, 0xfffe))
        self.assertParses("-16", (0x1f, 0xfff0))

    def test_short_literals(self):
        self.assertParses("-0x01", (0x20, None))
        self.assertParses("0", (0x21, None))
        self.assertParses("0x1e", (0x3f, None))
        self.assertParses("0b11", (0x24, None))


class TestParseInstructions(unittest.TestCase):
    def setUp(self):
        self.parser = AssemblyParser()
        self.parse = self.parser.parse

    def assertParses(self, given, expected):
        self.assertEquals(self.parse(given), [from_opcode(*expected[:3])] +
                expected[3:])

    def assertEmpty(self, given):
        self.assertEquals(self.parse(given), [])

    def assertOp(self, given, expected):
        self.assertEquals(self.parser.opcode(given), expected)

    def test_parse_SET(self):
        self.assertOp("SET", 0x1)

    def test_parse_ADD(self):
        self.assertOp("ADD", 0x2)

    def test_parse_SUB(self):
        self.assertOp("SUB", 0x3)

    def test_parse_MUL(self):
        self.assertOp("MUL", 0x4)

    def test_parse_DIV(self):
        self.assertOp("DIV", 0x5)

    def test_parse_MOD(self):
        self.assertOp("MOD", 0x6)

    def test_parse_SHL(self):
        self.assertOp("SHL", 0x7)

    def test_parse_SHR(self):
        self.assertOp("SHR", 0x8)

    def test_parse_AND(self):
        self.assertOp("AND", 0x9)

    def test_parse_BOR(self):
        self.assertOp("BOR", 0xa)

    def test_parse_XOR(self):
        self.assertOp("XOR", 0xb)

    def test_parse_IFE(self):
        self.assertOp("IFE", 0xc)

    def test_parse_IFN(self):
        self.assertOp("IFN", 0xd)

    def test_parse_IFG(self):
        self.assertOp("IFG", 0xe)

    def test_parse_IFB(self):
        self.assertOp("IFB", 0xf)

    def test_lowercase_ops(self):
        self.assertOp("ifb", 0xf)
        self.assertOp("shr", 0x8)
        self.assertOp("and", 0x9)
        self.assertOp("bor", 0xa)
        self.assertOp("XOR", 0xb)

    def test_instruction(self):
        self.assertParses("SET A, 0x30", [0x1, 0x0, 0x1f, 0x30])
        self.assertParses("SET A 0x30", [0x1, 0x0, 0x1f, 0x30])
        self.assertParses("SET I, 10", [0x1, 0x06, 0x2a])
        self.assertParses("SUB A, [0x1000]", [0x3, 0x0, 0x1e, 0x1000])
        self.assertParses("IFN A, 0x10", [0xd, 0x0, 0x30])

    def test_instruction_spaces(self):
        self.assertParses("SET A,0x30", [0x1, 0x0, 0x1f, 0x30])

    def test_spaces_in_brackets(self):
        a = self.parser.parse("SET A, [0x30+A]")
        b = self.parser.parse("SET A, [0x30 + A]")
        self.assertEquals(a, b)
        c = self.parser.parse("SET [0x30+A], A")
        d = self.parser.parse("SET [0x30 + A], A")
        self.assertEquals(c, d)
        e = self.parser.parse("SET [0x30+A], [0x0+J]")
        f = self.parser.parse("SET [0x30 + A], [0x0 + J]")
        self.assertEquals(e, f)

    def test_spaces_in_brackets_nonbasic(self):
        a = self.parser.parse("JSR [0x30+A]")
        b = self.parser.parse("JSR [0x30 + A]")
        self.assertEquals(a, b)

    def test_nonbasic_instruction(self):
        self.assertParses("JSR, 0x0002", [0x0, 0x01, 0x22])
        self.assertParses("JSR 0x0002", [0x0, 0x01, 0x22])

    def test_comments(self):
        self.assertParses("SET I, 10; comment", [0x1, 0x06, 0x2a])
        self.assertParses("SET I, 10;comment", [0x1, 0x06, 0x2a])
        self.assertParses("SET I, 10 ;comment", [0x1, 0x06, 0x2a])
        self.assertParses("SET I, 10 ; comment", [0x1, 0x06, 0x2a])

    def test_ignores(self):
        self.assertParses(" SET A, 0x30   ", [0x1, 0x0, 0x1f, 0x30])
        self.assertParses("\t SET I, 10 ; hi", [0x1, 0x06, 0x2a])
        self.assertEmpty("; hi comment")
        self.assertEmpty("    ;comment")
        self.assertEmpty("\t      ")

    def test_labels(self):
        self.assertParses("SET PC, label", [0x1, 0x1c, 0x1f, "label"])
        self.assertParses("SET A, label", [0x1, 0x00, 0x1f, "label"])
        self.assertParses("JSR testsub", [0x0, 0x01, 0x1f, "testsub"])

    def test_parse_text(self):
        lines = """
                SET A, 0x30        ; 
                SET [0x1000], 0x20 ; wooh , comment
                SUB A, [0x1000]

                IFN A, 0x10
        """.split("\n")
        self.assertEqual(self.parser.parse_tree(lines), [0x7c01, 0x0030,
            0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d])

    def test_label_definition(self):
        instruction = self.parser.parse(":start set A, 0x30")
        self.assertIn(("start", instruction), self.parser.labels)
        instruction = self.parser.parse("set A, 0x30")
        self.assertEquals(instruction, [0x7c01, 0x0030])

    def test_tricky_labels(self):
        instruction = self.parser.parse_tree([":set set set set"])
        # should be the same as set 0, 0.
        self.assertEquals(instruction, [0x7df1, 0, 0])

    def test_parse_text_with_labels(self):
        lines = """
                SET A, 0x30        ; 
                SET [0x1000], 0x20 ; wooh , comment
                SUB A, [0x1000]
                IFN A, 0x10
        :crash  SET PC, crash
        """.split("\n")
        self.assertEqual(self.parser.parse_tree(lines), [0x7c01, 0x0030,
            0x7de1, 0x1000, 0x0020, 0x7803, 0x1000, 0xc00d, 0x7dc1, 0x0008])

    def test_dat(self):
        assembly = "dat 0x30"
        self.assertEqual(self.parser.parse(assembly), [0x0030])

    def test_dat_multiple(self):
        assembly = "dat 0x30, 0x48"
        self.assertEqual(self.parser.parse(assembly), [0x0030, 0x048])
        assembly = "dat 0x30,0x48"
        self.assertEqual(self.parser.parse(assembly), [0x0030, 0x048])
        assembly = "dat 0x30 0x48, 1"
        self.assertEqual(self.parser.parse(assembly), [0x0030, 0x048, 1])

    def test_dat_text(self):
        assembly = ["dat 0x30, 0x48"]
        self.assertEqual(self.parser.parse_tree(assembly), [0x0030, 0x048])

    def test_dat_label(self):
        assembly = ["dat 0x30, label"]
        self.assertEqual(self.parser.parse_tree(assembly), [0x0030, "label"])

    def test_dat_string(self):
        assembly = ["dat \"ab\""]
        self.assertEqual(self.parser.parse_tree(assembly), [ord("a"), ord("b"),])
        assembly = ["dat \"a\", 0"]
        self.assertEqual(self.parser.parse_tree(assembly), [ord("a"), 0])
        assembly = ["dat 0, \"b\""]
        self.assertEqual(self.parser.parse_tree(assembly), [0, ord("b")])
        assembly = ["dat 0, 'b'"]
        self.assertEqual(self.parser.parse_tree(assembly), [0, ord("b")])

    def test_dat_string_quotes(self):
        assembly = [r'dat "a\""']
        self.assertEqual(self.parser.parse_tree(assembly), [ord("a"),
            ord('"'),])

    def test_data_label(self):
        assembly = [':data dat data']
        self.assertEqual(self.parser.parse_tree(assembly), [0])

    @unittest.expectedFailure
    def test_dat_string_commas(self):
        assembly = [r'dat "a,b"']
        self.assertEqual(self.parser.parse_tree(assembly), [ord("a"),
            ord(","), ord('b'),])

    @unittest.expectedFailure
    def test_dat_string_spaces(self):
        assembly = [r'dat "a b"']
        self.assertEqual(self.parser.parse_tree(assembly), [ord("a"),
            ord(" "), ord('b'),])

    @unittest.expectedFailure
    def test_label_plus_literal(self):
        lines = ":start set PC, start + 0xffff"
        self.assertEqual(self.parser.parse_tree([lines]), [0x7dc1, 0xffff])

    def test_label_pointer(self):
        lines = ":start set PC, [start]"
        self.assertEqual(self.parser.parse_tree([lines]), [0x79c1, 0x0000])

    @unittest.expectedFailure
    def test_label_plus_literal_pointer(self):
        lines = ":start set PC, [start + 0xffff]"
        self.assertEqual(self.parser.parse_tree([lines]), [0x79c1, 0xffff])

    def test_label_plus_register(self):
        lines = ":start set PC, [start + A]"
        self.assertEqual(self.parser.parse_tree([lines]), [0x41c1, 0x0000])

    def test_parse_lots_of_text(self):
        "Make sure the parser doesn't choke."
        lines = """
; Try some basic stuff
              SET A, 0x30              ; 7c01 0030
              SET [0x1000], 0x20       ; 7de1 1000 0020
              SUB A, [0x1000]          ; 7803 1000
              IFN A, 0x10              ; c00d 
                 SET PC, crash         ; 7dc1 001a [*]
              
; Do a loopy thing
              SET I, 10                ; a861
              SET A, 0x2000            ; 7c01 2000
:loop         SET [0x2000+I], [A]      ; 2161 2000
              SUB I, 1                 ; 8463
              IFN I, 0                 ; 806d
                 SET PC, loop          ; 7dc1 000d [*]

; Call a subroutine
              SET X, 0x4               ; 9031
              JSR testsub              ; 7c10 0018 [*]
              SET PC, crash            ; 7dc1 001a [*]

:testsub      SHL X, 4                 ; 9037
              SET PC, POP              ; 61c1
                
; Hang forever. X should now be 0x40 if everything went right.
:crash        SET PC, crash            ; 7dc1 001a [*]
        """.split("\n")
        self.parser.parse_tree(lines)
