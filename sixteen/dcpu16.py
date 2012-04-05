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

        # this is a dictionary of value codes to pairs of setters and getters
        # setters take a single argument and then set that value to the
        # argument; getters don't take any arguments and return that value.
        self.values = {
            0x1f: self.next_word(),
        }
        
        # add setters and getters for all the registers
        for n, r in zip(xrange(0x08), ["A", "B", "C", "X", "Y", "Z", "I", "J"]):
            self.values[n] = self.register(r)

        # add setters and getters for the short literals
        for n in xrange(0x20, 0x40):
            self.values[n] = self.short_literal(n - 0x20)
        

    def __getitem__(self, n):
        "Get the word at a given address."
        return self.RAM[n] or Word.from_hex("0000")

    def __setitem__(self, n, hex_value):
        "Set the word at a given address to a hex value."
        self.RAM[n] = Word.from_hex(hex_value)

    def dump(self):
        "Return a friendly dump of the RAM."
        return [w or "0000" for w in self.RAM]

    def cycle(self):
        pointer = self.registers["PC"]
        self.registers["PC"] += 1
        o, a, b = self.RAM[pointer].as_opcode()
        getattr(self, self.opcodes[o])(a, b)

    # values:
    def register(self, r):
        "Given the name of a register, return a setter and a getter for it."
        def setter(x):
            self.registers[r] = x
        def getter():
            return self.registers[r]
        return setter, getter

    def next_word(self):
        "Return a setter and a getter for the next word after the PC."
        def getter():
            value = self.RAM[self.registers["PC"]]
            self.registers["PC"] += 1
            return value.as_literal()
        def setter(k):
            # should this do anything?
            return None
        return setter, getter

    def short_literal(self, n):
        """Given an integer, make a getter that returns it and a setter that
        does nothing.

        From the docs:
        'If any instruction tries to assign a literal value, the assignment
        fails silently. Other than that, the instruction behaves as normal.'
        """
        def getter():
            return n
        def setter(x):
            pass
        return setter, getter

    # opcodes:
    def SET(self, a, b):
        setter, _ = self.values[a]
        _, getter = self.values[b]
        setter(getter())
