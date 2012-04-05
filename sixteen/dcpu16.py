# -*- coding: utf-8 -*-

from sixteen.words import Word


class DCPU16(object):
    opcodes = {
        0x00: None,
        0x01: "SET", 0x02: "ADD", 0x03: "SUB", 0x04: "MUL", 0x05: "DIV",
        0x06: "MOD", 0x07: "SHL", 0x08: "SHR", 0x09: "AND", 0x0a: "BOR",
        0x0b: "XOR", 0x0c: "IFE", 0x0d: "IFN", 0x0e: "IFG", 0x0f: "IFB",
    }

    _registers = {
        # basic registers
        "A": 0x0000, "B": 0x0000, "C": 0x0000, "X": 0x0000, "Y": 0x0000,
        "Z": 0x0000, "I": 0x0000, "J": 0x0000,
        # special registers
        "PC": 0x000, "SP": 0xffff, "O": 0x0000,
    }

    def __init__(self):
        # initialize RAM with empty words. None will be treated as empty 0000
        # words everywhere, because having 0x10000 Words around is expensive
        # right now.
        self.RAM = [None] * 0x10000
        # copy my own `registers` dict.
        self.registers = self._registers.copy()

    def __getitem__(self, n):
        "Get the word at a given address."
        return self.RAM[n] or Word.from_hex("0000")

    def __setitem__(self, n, hex_value):
        "Set the word at a given address to a hex value."
        self.RAM[n] = Word.from_hex(hex_value)

    def dump(self):
        "Return a friendly dump of the RAM."
        return [w or "0000" for w in self.RAM]
