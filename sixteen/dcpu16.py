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
    def opcode(fn):
        """This is a decorator that unpacks the setters and getters for a given
        value and passes them to the decorated function. This simplifies things
        a lot and makes for much much less duplicated code.

        Each decorated function gets the setter for its first argument and the
        getters for both arguments. I don't think any of them use the second
        setter.
        """
        def op(self, a_n, b_n):
            a_setter, a_getter = self.values[a_n]
            b_setter, b_getter = self.values[b_n]
            return fn(self, a_setter, a_getter, b_getter)
        return op

    @opcode
    def SET(self, setter, a, b):
        "0x1: SET a, b - sets a to b"
        setter(b())

    @opcode
    def ADD(self, setter, a, b):
        """0x2: ADD a, b - sets a to a+b, sets O to 0x0001 if there's an
        overflow, 0x0 otherwise.
        """
        div, result = divmod(a() + b(), len(self.RAM))
        setter(result)
        # overflow is either 0x0000 or 0x0001
        self.registers["O"] = int(div > 0)

    @opcode
    def SUB(self, setter, a, b):
        """0x3: SUB a, b - sets a to a-b, sets O to 0xffff if there's an
        underflow, 0x0 otherwise.
        """
        div, result = divmod(a() - b(), len(self.RAM))
        setter(result)
        # overflow is either 0x0000 or 0xffff
        self.registers["O"] = int(div < 0) and 0xffff

    @opcode
    def AND(self, setter, a, b):
        "0x9: AND a, b - sets a to a&b"
        setter(a() & b())

    @opcode
    def BOR(self, setter, a, b):
        "0xa: BOR a, b - sets a to a|b."
        setter(a() | b())

    @opcode
    def XOR(self, setter, a, b):
        "0xb: XOR a, b - sets a to a^b."
        setter(a() ^ b())

    @opcode
    def IFE(self, _, a, b):
        "0xc: IFE a, b - performs next instruction only if a==b."
        if a() != b():
            self.registers["PC"] += 1

    @opcode
    def IFN(self, _, a, b):
        "0xd: IFN a, b - performs next instruction only if a!=b."
        if a() == b():
            self.registers["PC"] += 1

    @opcode
    def IFG(self, _, a, b):
        "0xe: IFG a, b - performs next instruction only if a>b."
        if not a() > b():
            self.registers["PC"] += 1

    @opcode
    def IFB(self, _, a, b):
        "0xf: IFB a, b - performs next instruction only if (a&b)!=0."
        if a() & b() == 0:
            self.registers["PC"] += 1

    @opcode
    def MUL(self, setter, a, b):
        "0x4: MUL a, b - sets a to a*b, sets O to ((a*b)>>16)&0xffff."
        # handle overflow
        overflow, result = divmod(a() * b(), len(self.RAM))
        setter(result)
        self.registers["O"] = overflow

    @opcode
    def DIV(self, setter, a, b):
        """0x5: DIV a, b - sets a to a/b, sets O to ((a<<16)/b)&0xffff. if
        b==0, sets a and O to 0 instead.
        """
        a_r, b_r = a(), b()
        setter(a_r // b_r)
        overflow = ((a_r << 16) / b_r) & (len(self.RAM) - 1)
        self.registers["O"] = overflow

    @opcode
    def MOD(self, setter, a, b):
        "0x6: MOD a, b - sets a to a%b. if b==0, sets a to 0 instead."
        setter(a() % b())

    @opcode
    def SHL(self, setter, a, b):
        "0x7: SHL a, b - sets a to a<<b, sets O to ((a<<b)>>16)&0xffff."
        total = a() << b()
        # mask away the high end for the actual value
        setter(total & 0xffff)
        # shift away the low end for the overflow
        self.registers["O"] = total >> 16

    @opcode
    def SHR(self, setter, a, b):
        "0x8: SHR a, b - sets a to a>>b, sets O to ((a<<16)>>b)&0xffff"
        a_r, b_r = a(), b()
        setter(a_r >> b_r)
        # shift left and mask away the low end for the overflow
        self.registers["O"] = (a_r << (16 - b_r)) & 0xffff
