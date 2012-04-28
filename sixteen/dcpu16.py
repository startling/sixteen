# -*- coding: utf-8 -*-

from sixteen.values import NextWord, NextWordPointer
from sixteen.words import as_opcode
from functools import wraps


def basic_opcode(fn):
    @wraps(fn)
    def opcode_wrapper(self, ram_iter, a, b):
        a_value = self.values[a](self.registers, self.ram, ram_iter)
        b_value = self.values[b](self.registers, self.ram, ram_iter)
        return fn(self, a_value, b_value)
    return opcode_wrapper


def set_value(fn):
    """A decorator simplifying basic operations that set their `a` value and
    possibly EX. Each should return a tuple of their value and, optionally,
    the value for EX.
    """
    @wraps(fn)
    def set_wrapper(self, a, b):
        t = fn(self, a.get(), b.get())
        update_registers, update_ram = a.set(t[0])
        if len(t) == 2:
            update_registers.update({"EX": t[1]})
        return update_registers, update_ram
    return set_wrapper


def special_opcode(fn):
    @wraps(fn)
    def opcode_wrapper(self, ram_iter, a):
        a_value = self.values[a](self.registers, self.ram, ram_iter)
        return fn(self, a_value)
    return opcode_wrapper


class DCPU16(object):
    # DCPU16 has 0x10000 cells
    cells = 0x10000

    # a class-attribute list of all of the register names.
    _registers = [
        # basic registers
        "A", "B", "C", "X", "Y", "Z", "I", "J",
        # special registers
        "PC", "SP", "EX", "IA"
    ]

    def __init__(self, hardware=None):
        # make a dictionary of all the registers of this class, initializing
        # them all to 0x0000.
        self.registers = dict((r, 0x0000) for r in self._registers)
        # initialize the hardware list
        self.hardware = hardware or []
        # initialize the RAM
        self.ram_init()
        
    def __getattr__(self, name):
        "If an attribute doesn't exist, try the registers."
        r = self.registers.get(name.upper())
        if r == None:
            raise AttributeError(name)
        else:
            return r

    def ram_init(self):
        "A function that sets the RAM of this CPU to its initial values."
        self.ram = [0x0000] * self.cells

    values = {
        0x1e: NextWordPointer,
        0x1f: NextWord,
    }

    def cycle(self):
        "Run for one instruction, returning the executed instruction."
        ram, consumed = self.ram_iter()
        # unpack the opcode, a, and b
        op, a, b = as_opcode(next(ram))
        # get the mnemonic and the method corresponding to it.
        mnemonic = self.operations.get(op)
        method = getattr(self, mnemonic)
        # run the method and decide what changes to do.
        register_changes, ram_changes = method(ram, a, b)
        # change all the registers
        for k, v in register_changes.iteritems():
            self.update_register(k, v)
        # change all the RAM
        for k, v in ram_changes.iteritems():
            self.update_ram(k, v)
        # increment the pc by len(consumed)
        self.registers["PC"] = (self.registers["PC"] + len(consumed)) % self.cells
        return consumed

    def update_register(self, name, value):
        # use modulus to take overflow and underflow into account
        self.registers[name] = value % self.cells

    def update_ram(self, addr, value):
        # use modulus to take overflow and underflow into account
        self.ram[addr % self.cells] = value % self.cells

    def ram_iter(self):
        """Return an iterator over this cpu's RAM and a list that will be updated
        whenever a value is drawn.
        """
        consumed = []
        def i():
            place = self.registers["PC"]
            while True:
                consumed.append(self.ram[place])
                yield self.ram[place]
                # increment the place counter, handling overflow if applicable.
                place += 1
                place %= self.cells
        return i(), consumed

    # a dictionary of opcode numbers to mnemonics
    operations = {
        0x00: "special", 0x01: "set", 0x02: "add", 0x03: "sub", 0x04: "mul",
        0x05: "mli", 0x06: "div", 0x07: "dvi", 0x08: "mod", 0x09: "and",
        0x0a: "bor", 0x0b: "xor", 0x0c: "shr", 0x0d: "asr", 0x0e: "shl",
        0x0f: "sti", 0x10: "ifb", 0x11: "ifc", 0x12: "ife", 0x13: "ifn",
        0x14: "ifg", 0x15: "ifa", 0x16: "ifl", 0x17: "ifu",
        0x1a: "adx", 0x1b: "sbx",
    }

    @basic_opcode
    @set_value
    def set(self, a, b):
        return b,

    @basic_opcode
    @set_value
    def add(self, a, b):
        overflow, result = divmod(a + b, self.cells)
        return result, int(overflow > 0)

    @basic_opcode
    @set_value
    def sub(self, a, b):
        overflow, result = divmod(a - b, self.cells)
        return result, overflow < 0 and 0xffff

    @basic_opcode
    @set_value
    def mul(self, a, b):
        overflow, result = divmod(a * b, self.cells)
        return result, overflow

    # a dict of nonbasic opcode numbers to mnemonics
    special_operations = {
        0x01: "jsr", 0x07: "hcf", 0x08: "int", 0x09: "iag", 0x0a: "ias",
        0x10: "hwn", 0x11: "hwq", 0x12: "hwi",
    }

    def special(self, ram_iter, o, a):
        "Pass special opcodes to their methods."
        mnemonic = self.special_operations.get(o)
        method = getattr(self, mnemonic)
        return method(ram_iter, a)
