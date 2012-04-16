# -*- coding: utf-8 -*-

from sixteen.words import as_opcode, from_hex
from sixteen.utilities import OpcodeError
from sixteen import boxes
from functools import wraps


class DCPU16(object):
    # DCPU16 has 0x10000 cells
    cells = 0x10000

    # Number of cycles for which this CPU has run.
    cycles = 0

    opcodes = {
        0x00: "SPEC",
        0x01: "SET", 0x02: "ADD", 0x03: "SUB", 0x04: "MUL", 0x05: "DIV",
        0x06: "MOD", 0x07: "SHL", 0x08: "SHR", 0x09: "AND", 0x0a: "BOR",
        0x0b: "XOR", 0x0c: "IFE", 0x0d: "IFN", 0x0e: "IFG", 0x0f: "IFB",
    }

    special_opcodes = {
        0x01: "JSR",
    }

    _registers = {
        # basic registers
        "A": 0x0000, "B": 0x0000, "C": 0x0000, "X": 0x0000, "Y": 0x0000,
        "Z": 0x0000, "I": 0x0000, "J": 0x0000,
        # special registers
        "PC": 0x000, "SP": 0x0000, "O": 0x0000,
    }
    
    SP = boxes.Register("SP")

    # this is a dictionary of value codes to classes that inherit from Box.
    # each of these classes get instantiated with this CPU and then have
    # .get and .set methods.
    values = {
        0x1e: boxes.NextWordAsPointer, 0x1f: boxes.NextWord,
        # values for PC, and O
        0x1c: boxes.Register("PC").as_value(),
        0x1d: boxes.Register("O").as_value(),
        # value for SP
        0x1b: SP.as_value(),
        # PEEK is just a register pointer to SP
        0x19: SP.as_pointer(),
        # PUSH and POP
        0x18: boxes.POP, 0x1a: boxes.PUSH,
    }
    
    # add Box classes for all the registers
    for n, r in zip(xrange(0x08), ["A", "B", "C", "X", "Y", "Z", "I", "J"]):
        register = boxes.Register(r)
        values[n] = register.as_value()
        # add register pointers
        values[n + 0x08] = register.as_pointer()
        # add [register + next word]s
        values[n + 0x10] = register.and_next_word()

    # add setters and getters for the short literals
    for n in xrange(0x20, 0x40):
        values[n] = boxes.ShortLiteral(n - 0x20)

    def __init__(self):
        # initialize RAM with empty words.
        self.RAM = [0x0000] * self.cells
        # copy my own `registers` dict.
        self.registers = self._registers.copy()

    def __getitem__(self, n):
        "Get the word at a given address."
        return self.RAM[n]

    def __setitem__(self, n, value):
        "Set the word at a given address to a hex value."
        # if we go over the limit, make it 0
        self.RAM[n] = value

    def parse_instruction(self, word, address=None):
        o, a_code, b_code = as_opcode(word)
        # if this is a special opcode...
        if o == 0x00:
            # arguments are switched for the special opcodes
            a = self.values[b_code](self)
            name = self.special_opcodes.get(a_code)
            if name == None:
                raise OpcodeError(o, address)
            # return the name and the arguments
            return name, (a,)
        else:
            a = self.values[a_code](self)
            b = self.values[b_code](self)
            name = self.opcodes.get(o)
            if name == None:
                raise OpcodeError(o, address)
            # return the name of the operation and the arguments
            return name, (a, b)

    def cycle(self):
        "Run for one cycle and return the operation and its arguments.."
        self.cycles += 1

        address = self.registers["PC"]
        op, args = self.parse_instruction(self.get_next(), address)
        getattr(self, op)(*args)
        # return the name of the operation and the arguments
        return op, args

    def get_next(self):
        "Increment the program counter and return its value."
        v = self.RAM[self.registers["PC"]]
        if self.registers["PC"] < len(self.RAM) - 1:
            self.registers["PC"] += 1
        else:
            self.registers["PC"] = 0x0000
        return v
    
    # opcodes:
    def SET(self, a, b):
        "0x1: SET a, b - sets a to b"
        a.set(b.get())

    def ADD(self, a, b):
        """0x2: ADD a, b - sets a to a+b, sets O to 0x0001 if there's an
        overflow, 0x0 otherwise.
        """
        div, result = divmod(a.get() + b.get(), len(self.RAM))
        a.set(result)
        self.registers["O"] = int(div > 0)

    def SUB(self, a, b):
        """0x3: SUB a, b - sets a to a-b, sets O to 0xffff if there's an
        underflow, 0x0 otherwise.
        """
        div, result = divmod(a.get() - b.get(), len(self.RAM))
        a.set(result)
        self.registers["O"] = int(div < 0) and 0xffff

    def AND(self, a, b):
        "0x9: AND a, b - sets a to a&b"
        a.set(a.get() & b.get())

    def BOR(self, a, b):
        "0xa: BOR a, b - sets a to a|b."
        a.set(a.get() | b.get())

    def XOR(self, a, b):
        "0xb: XOR a, b - sets a to a^b."
        a.set(a.get() ^ b.get())

    def IFX(fn):
        """A decorator for all of the IF operations. They can just return a boolean;
        if it's False, jump ahead an instruction.
        """
        @wraps(fn)
        def op(self, a, b):
            boolean = fn(self, a, b)
            if not boolean:
                # get the arguments from the next word
                _, n_a, n_b = as_opcode(self.RAM[self.registers["PC"]])
                # compute the length of the next word's values.
                length = self.values[n_a].consumes + self.values[n_b].consumes
                # jump ahead that many words.
                self.registers["PC"] += 1 + length
        return op

    @IFX
    def IFE(self, a, b):
        "0xc: IFE a, b - performs next instruction only if a==b."
        return a.get() == b.get()

    @IFX
    def IFN(self, a, b):
        "0xd: IFN a, b - performs next instruction only if a!=b."
        return a.get() != b.get()

    @IFX
    def IFG(self, a, b):
        "0xe: IFG a, b - performs next instruction only if a>b."
        return a.get() > b.get()

    @IFX
    def IFB(self, a, b):
        "0xf: IFB a, b - performs next instruction only if (a&b)!=0."
        return a.get() & b.get() != 0

    def MUL(self, a, b):
        "0x4: MUL a, b - sets a to a*b, sets O to ((a*b)>>16)&0xffff."
        # handle overflow
        overflow, result = divmod(a.get() * b.get(), len(self.RAM))
        a.set(result)
        self.registers["O"] = overflow

    def DIV(self, a, b):
        """0x5: DIV a, b - sets a to a/b, sets O to ((a<<16)/b)&0xffff. if
        b==0, sets a and O to 0 instead.
        """
        a_r, b_r = a.get(), b.get()
        if b_r == 0:
            a.set(0)
            overflow = 0
        else:
            a.set(a_r // b_r)
            overflow = ((a_r << 16) / b_r) & (len(self.RAM) - 1)
        self.registers["O"] = overflow

    def MOD(self, a, b):
        "0x6: MOD a, b - sets a to a%b. if b==0, sets a to 0 instead."
        a_r = a.get()
        b_r = b.get()
        if b_r == 0:
            a.set(0)
        else:
            a.set(a_r % b_r)

    def SHL(self, a, b):
        "0x7: SHL a, b - sets a to a<<b, sets O to ((a<<b)>>16)&0xffff."
        a_r, b_r = a.get(), b.get()
        total = a_r << b_r
        # mask away the high end for the actual value
        a.set(total & 0xffff)
        # shift away the low end for the overflow
        self.registers["O"] = ((a_r << b_r ) >> 16) & 0xffff

    def SHR(self, a, b):
        "0x8: SHR a, b - sets a to a>>b, sets O to ((a<<16)>>b)&0xffff"
        a_r, b_r = a.get(), b.get()
        a.set(a_r >> b_r)
        # shift left and mask away the low end for the overflow
        self.registers["O"] = ((a_r << 16) >> b_r) & 0xffff

    # Special operations
    def JSR(self, a):
        """JSR a - pushes the address of the next instruction to the stack, then
        sets PC to a.
        """
        # push the next word to the stack
        self.registers["SP"] -= 1
        # handle underflow
        if self.registers["SP"] < 0:
            self.registers["SP"] = len(self.RAM) + self.registers["SP"]
        self.RAM[self.registers["SP"]] = self.registers["PC"]
        # and then set the program counter to A
        self.registers["PC"] = a.get()
