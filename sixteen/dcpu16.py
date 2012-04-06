# -*- coding: utf-8 -*-

from sixteen.words import as_opcode, from_hex


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
        self.RAM = [0x0000] * 0x10000
        # copy my own `registers` dict.
        self.registers = self._registers.copy()

        # this is a dictionary of value codes to pairs of setters and getters
        # setters take a single argument and then set that value to the
        # argument; getters don't take any arguments and return that value.
        self.values = {
            0x1e: self.next_word_pointer(), 0x1f: self.next_word(),
            # values for SP, PC, and O
            0x1b: self.register("SP"), 0x1c: self.register("PC"),
            0x1d: self.register("O"),
            # POP and PUSH
            0x18: self.POP(), 0x1a: self.PUSH(),
            # PEEK is just a register pointer to SP
            0x19: self.register_pointer("SP"),
        }
        
        # add setters and getters for all the registers
        for n, r in zip(xrange(0x08), ["A", "B", "C", "X", "Y", "Z", "I", "J"]):
            self.values[n] = self.register(r)
            # add register pointers
            self.values[n + 0x08] = self.register_pointer(r)
            # add [register + next word]s
            self.values[n + 0x10] = self.register_plus_next_word(r)

        # add setters and getters for the short literals
        for n in xrange(0x20, 0x40):
            self.values[n] = self.short_literal(n - 0x20)
        

    def __getitem__(self, n):
        "Get the word at a given address."
        return self.RAM[n] or 0x0000

    def __setitem__(self, n, value):
        "Set the word at a given address to a hex value."
        # if we go over the limit, make it 0
        self.RAM[n] = value

    def dump(self):
        "Return a friendly dump of the RAM."
        return self.RAM

    def cycle(self):
        "Run for one cycle."
        word = self.get_next()
        o, a, b = as_opcode(word)
        getattr(self, self.opcodes[o])(a, b)

    def get_next(self):
        "Increment the program counter and return its value."
        v = self.RAM[self.registers["PC"]]
        self.registers["PC"] += 1
        return v
    
    # values:
    def register(self, r):
        "Given the name of a register, return a setter and a getter for it."
        def setter(x):
            self.registers[r] = x
        def getter():
            return self.registers[r]
        return setter, getter

    def register_pointer(self, r):
        """Given the name of a register, return a setter and getter for where
        it points.
        """
        def setter(x):
            self.RAM[self.registers[r]] = x
        def getter():
            return self.RAM[self.registers[r]]
        return setter, getter

    def register_plus_next_word(self, r):
        "Given the name of a register, return [next word + register]."
        def getter():
            address = self.get_next() + self.registers[r]
            return self.RAM[address]
        def setter(x):
            address = self.get_next() + self.registers[r]
            self.RAM[address] = x
        return setter, getter

    def next_word_pointer(self):
        "Return a setter and a getter for the value at next word."
        def getter():
            return self.RAM[self.get_next()]
        def setter(x):
            self.RAM[self.get_next()] = x
        return setter, getter

    def next_word(self):
        "Return a setter and a getter for the next word after the PC."
        def getter():
            return self.get_next()
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

    def POP(self):
        def getter():
            v = self.RAM[self.registers["SP"]]
            self.registers["SP"] += 1
            # handle overflow
            if self.registers["SP"] == len(self.RAM) - 1:
                self.registers["SP"] = 0x0000
            return v
        def setter(x):
            self.RAM[self.registers["SP"]] = x
            self.registers["SP"] += 1
            # handle overflow
            if self.registers["SP"] == len(self.RAM) - 1:
                self.registers["SP"] = 0x0000
        return setter, getter

    def PUSH(self):
        def getter():
            self.registers["SP"] -= 1
            # handle underflow
            if self.registers["SP"] < 0:
                self.registers["SP"] = len(self.RAM) - 1
            return self.RAM[self.registers["SP"]]
        def setter(x):
            self.registers["SP"] -= 1
            # handle underflow
            if self.registers["SP"] < 0:
                self.registers["SP"] = len(self.RAM) - 1
            self.RAM[self.registers["SP"]] = x
        return setter, getter

    # opcodes:
    def SET(self, a, b):
        setter, _ = self.values[a]
        _, getter = self.values[b]
        setter(getter())

    def ADD(self, a, b):
        a_set, a_get = self.values[a]
        _, b_get = self.values[b] 
        result = a_get() + b_get()
        # handle overflow
        div, result = divmod(result, len(self.RAM))
        overflow = int(div > 0)
        a_set(result)
        self.registers["O"] = overflow

    def SUB(self, a, b):
        a_set, a_get = self.values[a]
        _, b_get = self.values[b] 
        result = a_get() - b_get()
        # handle overflow
        div, result = divmod(result, len(self.RAM))
        overflow = int(div < 0) and 0xffff
        a_set(result)
        self.registers["O"] = overflow

    def AND(self, a, b):
        a_set, a_get = self.values[a]
        _, b_get = self.values[b] 
        a_set(a_get() & b_get())

    def BOR(self, a, b):
        a_set, a_get = self.values[a]
        _, b_get = self.values[b] 
        a_set(a_get() | b_get())

    def XOR(self, a, b):
        a_set, a_get = self.values[a]
        _, b_get = self.values[b] 
        a_set(a_get() ^ b_get())

    def IFE(self, a, b):
        _, a_get = self.values[a]
        _, b_get = self.values[b]
        if a_get() != b_get():
            self.registers["PC"] += 1

    def IFN(self, a, b):
        _, a_get = self.values[a]
        _, b_get = self.values[b]
        if a_get() == b_get():
            self.registers["PC"] += 1

    def IFG(self, a, b):
        _, a_get = self.values[a]
        _, b_get = self.values[b]
        if not a_get() > b_get():
            self.registers["PC"] += 1

    def IFB(self, a, b):
        _, a_get = self.values[a]
        _, b_get = self.values[b]
        if a_get() & b_get() == 0:
            self.registers["PC"] += 1

    def MUL(self, a, b):
        a_set, a_get = self.values[a]
        _, b_get = self.values[b]
        result = a_get() * b_get()
        # handle overflow
        overflow, result = divmod(result, len(self.RAM))
        a_set(result)
        self.registers["O"] = overflow

    def DIV(self, a, b):
        a_set, a_get = self.values[a]
        _, b_get = self.values[b]
        result = a_get() // b_get()
        a_set(result)
