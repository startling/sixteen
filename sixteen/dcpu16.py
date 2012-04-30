# -*- coding: utf-8 -*-

from sixteen.values import NextWord, NextWordPointer, RegisterValue, \
    RegisterPointer, RegisterPlusNextWord, Literal, POPorPUSH
from sixteen.states import State
from sixteen.bits import as_instruction, as_signed, from_signed
from functools import wraps


def basic_opcode(fn):
    @wraps(fn)
    def opcode_wrapper(self, state, b, a):
        a_value = self.values[a](state, True)
        b_value = self.values[b](state, False)
        return fn(self, state, b_value, a_value)
    return opcode_wrapper


def signed(fn):
    """A decorator for basic operations that casts the arguments to signed
    (two's complement) integers and casts the single returned value back to
    unsigned.
    """
    @set_value
    @wraps(fn)
    def signed_wrapper(self, b_unsigned, a_unsigned):
        b = as_signed(b_unsigned)
        a = as_signed(a_unsigned)
        value = from_signed(fn(self, b, a))
        # handle overflow for signed values
        overflow, result = divmod(value, self.cells)
        # NOTE: this clears overflow for all signed operations.
        # this may be wrong; I don't care right now.
        return value, overflow

    return signed_wrapper


def set_value(fn):
    """A decorator simplifying basic operations that set their `a` value and
    possibly EX. Each should return a tuple of their value and, optionally,
    the value for EX.
    """
    @basic_opcode
    @wraps(fn)
    def set_wrapper(self, state, b, a):
        t = fn(self, b.get(), a.get())
        b.set(t[0])
        if len(t) == 2:
            state.registers["EX"] = t[1]
    return set_wrapper


def conditional(fn):
    """A decorator for wrapping conditional basic operations. The decorated
    function should just return a boolean of whether to continue or to skip.
    """
    @wraps(fn)
    def conditional_wrapper(self, state, b, a):
        # initialize the values
        a_value = self.values[a](state, True)
        b_value = self.values[b](state, False)
        if fn(self, b_value.get(), a_value.get()):
            # if the predicate returns True, we continue as usuaul
            return
        else:
            #TODO: chained conditionals
            # otherwise, figure out where the next instruction will be
            next_instruction = state.registers["PC"] + len(state.consumed)
            # run it to decide what words it consumes
            next_consumed = self.get_instruction(next_instruction).consumed
            # and then skip ahead past it.
            pc = (next_instruction + len(next_consumed)) % self.cells
            state.registers["PC"] = pc 
    return conditional_wrapper


def signed_conditional(fn):
    @conditional
    @wraps(fn)
    def signed_conditional_wrapper(self, b, a):
        return fn(self, as_signed(b), as_signed(a))
    return signed_conditional_wrapper


def special_opcode(fn):
    @wraps(fn)
    def opcode_wrapper(self, state, a):
        a_value = self.values[a](state, True)
        return fn(self, state, a_value)
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
        # POP/PUSH 
        0x18: POPorPUSH,
        # PEEK is just [SP]
        0x19: RegisterPointer.named("SP"),
        # [SP + next word] / PICK
        0x1a: RegisterPlusNextWord.named("SP"),
        # SP, PC, and EX as registers
        0x1b: RegisterValue.named("SP"), 0x1c: RegisterValue.named("PC"),
        0x1d: RegisterValue.named("EX"),
        # next word pointers and literals
        0x1e: NextWordPointer,
        0x1f: NextWord,
    }

    # set all the ordinary register values
    for n, name in enumerate(["A", "B", "C", "X", "Y", "Z", "I", "J"]):
        values[n] = RegisterValue.named(name)
        values[n + 0x08] = RegisterPointer.named(name)
        values[n + 0x10] = RegisterPlusNextWord.named(name)
    # set all of the short literals
    values[0x20] = Literal(0xffff)
    for n in xrange(1, 31):
        values[0x21 + n] = Literal(n)


    def get_instruction(self, location=None):
        state = State(self, location)
        # unpack the opcode, a, and b
        op, b, a = as_instruction(next(state.ram_iter))
        # get the mnemonic and the method corresponding to it.
        mnemonic = self.operations.get(op)
        method = getattr(self, mnemonic)
        # run the method and decide what changes to do.
        method(state, b, a)
        return state
        

    def cycle(self):
        "Run for one instruction, returning the executed instruction."
        state = self.get_instruction()
        # change all the registers
        for k, v in state.registers.iteritems():
            self.update_register(k, v)
        # change all the RAM
        for k, v in state.ram.iteritems():
            self.update_ram(k, v)
        # increment the pc by len(consumed)
        self.registers["PC"] = ((self.registers["PC"] + len(state.consumed))
            % self.cells)
        return state.consumed

    def update_register(self, name, value):
        # use modulus to take overflow and underflow into account
        self.registers[name] = value % self.cells

    def update_ram(self, addr, value):
        # use modulus to take overflow and underflow into account
        self.ram[addr % self.cells] = value % self.cells

    def ram_iter(self, location=None):
        """Return an iterator over this cpu's RAM and a list that will be updated
        whenever a value is drawn.
        """
        consumed = []
        def i():
            place = location or self.registers["PC"]
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
        0x05: "mli", 0x06: "div", 0x07: "dvi", 0x08: "mod", 0x09: "mdi",
        0x0a: "AND", 0x0b: "bor", 0x0c: "xor", 0x0d: "shr", 0x0e: "asr",
        0x0f: "shl", 0x10: "ifb", 0x11: "ifc", 0x12: "ife", 0x13: "ifn",
        0x14: "ifg", 0x15: "ifa", 0x16: "ifl", 0x17: "ifu", 0x1a: "adx",
        0x1b: "sbx", 0x1e: "sti", 0x1f: "std"
    }

    @set_value
    def set(self, b, a):
        return a,

    @set_value
    def add(self, b, a):
        overflow, result = divmod(b + a, self.cells)
        return result, int(overflow > 0)

    @set_value
    def sub(self, b, a):
        overflow, result = divmod(b - a, self.cells)
        return result, overflow < 0 and 0xffff

    @set_value
    def mul(self, b, a):
        overflow, result = divmod(b * a, self.cells)
        return result, overflow

    @signed
    def mli(self, b, a):
        return b * a

    @set_value
    def div(self, b, a):
        if a == 0:
            return 0, 0
        else:
            return b // a, ((b << 16) // a) & 0xffff

    @signed
    def dvi(self, b, a):
        return b // a

    @set_value
    def mod(self, b, a):
        return b % a,

    @signed
    def mdi(self, b, a):
        # if notch changes it to true modulus, it'll be
        # > return b % a
        return b % a - a

    @set_value
    def AND(self, b, a):
        return b & a,

    @set_value
    def bor(self, b, a):
        return b | a,
    
    @set_value
    def xor(self, b, a):
        return b ^ a,

    @set_value
    def shr(self, b, a):
        return b >> a, ((b << 16) >> a) & 0xffff

    @signed
    def asr(self, b, a):
        return b >> a

    @set_value
    def shl(self, b, a):
        overflow, result = divmod(b << a, self.cells)
        return result, overflow

    @conditional
    def ifb(self, b, a):
        return (b & a) != 0

    @conditional
    def ifc(self, b, a):
        return (b & a) == 0

    @conditional
    def ife(self, b, a):
        return b == a

    @conditional
    def ifn(self, b, a):
        return b != a

    @conditional
    def ifg(self, b, a):
        return b > a

    @signed_conditional
    def ifa(self, b, a):
        return b > a

    @conditional
    def ifl(self, b, a):
        return b < a

    @signed_conditional
    def ifu(self, b, a):
        return b < a

    @set_value
    def adx(self, b, a):
        overflow, result = divmod(b + a + self.registers["EX"], self.cells)
        return result, int(overflow > 0)

    @set_value
    def sbx(self, b, a):
        overflow, result = divmod(b - a + self.registers["EX"], self.cells)
        return result, overflow and 0xffff

    @basic_opcode
    def sti(self, state, b, a):
        b.set(a.get())
        state.registers["I"] += 1
        state.registers["J"] += 1

    @basic_opcode
    def std(self, state, b, a):
        b.set(a.get())
        state.registers["I"] -= 1
        state.registers["J"] -= 1

    # a dict of nonbasic opcode numbers to mnemonics
    special_operations = {
        0x01: "jsr", 0x08: "int", 0x09: "iag", 0x0a: "ias", 0x10: "hwn",
        0x11: "hwq", 0x12: "hwi",
    }

    def special(self, state, o, a):
        "Pass special opcodes to their methods."
        mnemonic = self.special_operations.get(o)
        method = getattr(self, mnemonic)
        return method(state, a)

    @special_opcode
    def jsr(self, state, a):
        state.push(state.registers["PC"])
        state.registers["PC"] = a.get()

    @special_opcode
    def iag(self, state, a):
        a.set(self.registers["IA"])

    @special_opcode
    def ias(self, state, a):
        state.registers["IA"] = a.get()
