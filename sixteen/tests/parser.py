# -*- coding: utf-8 -*-

import unittest
from sixteen.parser import AssemblyParser


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = AssemblyParser()
        self.parse = self.parser.parse

    def assertParses(self, given, expected):
        self.assertEquals(self.parse(given), expected)

    def test_parse_registers(self):
        self.assertParses("A", 0x00)
        self.assertParses("B", 0x01)
        self.assertParses("Y", 0x04)
        self.assertParses("J", 0x07)
