# -*- coding: utf-8 -*-

from sixteen.values import NextWord, NextWordPointer, RegisterValue, \
    RegisterPointer, RegisterPlusNextWord, Literal, POPorPUSH
from sixteen.utilities import OpcodeError
from sixteen.states import State
from sixteen.bits import as_instruction, as_signed, from_signed
from functools import wraps


def signed(fn):
    """A decorator for basic operations that casts the arguments to signed
    (two's complement) integers and casts the single returned value back to
    unsigned.
    """
    @set_value
    @wraps(fn)
    def signed_wrapper(self, state, b_unsigned, a_unsigned):
        b = as_signed(b_unsigned)
        a = as_signed(a_unsigned)
        value = from_signed(fn(self, state, b, a))
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
    @wraps(fn)
    def set_wrapper(self, state, b, a):
        t = fn(self, state, b.get(), a.get())
        if len(t) == 2:
            state.registers["EX"] = t[1]
        b.set(t[0])
    return set_wrapper


def conditional(fn):
    """A decorator for wrapping conditional basic operations. The decorated
    function should just return a boolean of whether to continue or to skip.
    """
    @wraps(fn)
    def conditional_wrapper(self, state, b, a):
        # initialize the values
        if fn(self, state, b.get(), a.get()):
            # if the predicate returns True, we continue as usuaul
            return
        else:
            pc = state.registers["PC"]
            while True:
                state.cycles += 1
                # run the next instruction so we can see how much it consumes
                _, _, skip_state = self.get_instruction(pc)
                pc = skip_state.registers["PC"]
                # if it's a conditional, continue
                if not self.is_conditional(skip_state.consumed[0]):
                    break
            # skip ahead to where that instruction stopped
            state.registers["PC"] = pc
    return conditional_wrapper


def signed_conditional(fn):
    @conditional
    @wraps(fn)
    def signed_conditional_wrapper(self, state, b, a):
        return fn(self, state, as_signed(b), as_signed(a))
    return signed_conditional_wrapper


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
        # initialize the queue and queuing
        self.queuing = False
        self.interrupt_queue = []
        # initialize cycle counting
        self.cycles = 0

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
    for n in xrange(0, 31):
        values[0x21 + n] = Literal(n)

    def get_instruction(self, location=None):
        state = State(self, location)
        # unpack the opcode, a, and b
        op, b, a = as_instruction(next(state.ram_iter))
        # get the mnemonic and the method corresponding to it.
        if op == 0:
            mnemonic = self.special_operations.get(b)
            if mnemonic is None:
                raise OpcodeError(b, location)
            a_value = self.values[a](state, True)
            arguments = (a_value,)
            state.dis = "{0} {1}".format(mnemonic, a_value.dis)
        else:
            mnemonic = self.operations.get(op)
            if mnemonic is None:
                raise OpcodeError(op, location)
            a_value = self.values[a](state, True)
            b_value = self.values[b](state, False)
            arguments = (b_value, a_value)
            state.dis = "{0} {1}, {2}".format(mnemonic, b_value.dis,
                    a_value.dis)
        method = getattr(self, mnemonic)
        # run the method and decide what changes to do.
        return method, arguments, state

    def cycle(self):
        "Run for one instruction, returning the executed instruction."
        method, arguments, state = self.get_instruction()
        method(state, *arguments)
        # hand hardware interrupts to devices
        for index in state.interrupts:
            device = self.hardware[index]
            device.on_interrupt(state.registers, state.ram)
        # allow each of the devices to interrupt
        #TODO: run queued interrupts
        for device in self.hardware:
            value = device.on_cycle(state.registers.changes, state.ram.changes)
            if value is not None:
                state.interrupt(value)
        # if there's anything in the queue...
        if state.interrupt_queue:
            state.do_interrupt(state.interrupt_queue.pop())
        # update queuing and the queue:
        self.interrupt_queue.extend(state.interrupt_queue)
        self.queuing = state.queuing
        # change all the registers
        for k, v in state.registers.iteritems():
            self.update_register(k, v)
        # change all the RAM
        for k, v in state.ram.iteritems():
            self.update_ram(k, v)
        # change the cycle counter
        self.cycles = state.cycles
        return state

    def update_register(self, name, value):
        # use modulus to take overflow and underflow into account
        self.registers[name] = value % self.cells

    def update_ram(self, addr, value):
        # use modulus to take overflow and underflow into account
        self.ram[addr % self.cells] = value % self.cells

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
    def set(self, state, b, a):
        state.cycles += 1
        return a,

    @set_value
    def add(self, state, b, a):
        state.cycles += 2
        overflow, result = divmod(b + a, self.cells)
        return result, int(overflow > 0)

    @set_value
    def sub(self, state, b, a):
        state.cycles += 2
        overflow, result = divmod(b - a, self.cells)
        return result, overflow < 0 and 0xffff

    @set_value
    def mul(self, state, b, a):
        state.cycles += 2
        overflow, result = divmod(b * a, self.cells)
        return result, overflow

    @signed
    def mli(self, state, b, a):
        state.cycles += 2
        return b * a

    @set_value
    def div(self, state, b, a):
        state.cycles += 3
        if a == 0:
            return 0, 0
        else:
            return b // a, ((b << 16) // a) & 0xffff

    @signed
    def dvi(self, state, b, a):
        state.cycles += 3
        return b // a

    @set_value
    def mod(self, state, b, a):
        state.cycles += 3
        if a == 0:
            return 0,
        else:
            return b % a,

    @signed
    def mdi(self, state, b, a):
        state.cycles += 3
        # if notch changes it to true modulus, it'll be
        # > return b % a
        return b % a - a

    @set_value
    def AND(self, state, b, a):
        state.cycles += 1
        return b & a,

    @set_value
    def bor(self, state, b, a):
        state.cycles += 1
        return b | a,

    @set_value
    def xor(self, state, b, a):
        state.cycles += 1
        return b ^ a,

    @set_value
    def shr(self, state, b, a):
        state.cycles += 1
        return b >> a, ((b << 16) >> a) & 0xffff

    @signed
    def asr(self, state, b, a):
        state.cycles += 1
        return b >> a

    @set_value
    def shl(self, state, b, a):
        state.cycles += 1
        overflow, result = divmod(b << a, self.cells)
        return result, overflow

    @conditional
    def ifb(self, state, b, a):
        state.cycles += 2
        return (b & a) != 0

    @conditional
    def ifc(self, state, b, a):
        state.cycles += 2
        return (b & a) == 0

    @conditional
    def ife(self, state, b, a):
        state.cycles += 2
        return b == a

    @conditional
    def ifn(self, state, b, a):
        state.cycles += 2
        return b != a

    @conditional
    def ifg(self, state, b, a):
        state.cycles += 2
        return b > a

    @signed_conditional
    def ifa(self, state, b, a):
        state.cycles += 2
        return b > a

    @conditional
    def ifl(self, state, b, a):
        state.cycles += 2
        return b < a

    @signed_conditional
    def ifu(self, state, b, a):
        state.cycles += 2
        return b < a

    def is_conditional(self, instruction):
        o, b, a = as_instruction(instruction)
        name = self.operations.get(o)
        return name is not None and name.startswith("if")

    @set_value
    def adx(self, state, b, a):
        state.cycles += 3
        overflow, result = divmod(b + a + state.registers["EX"], self.cells)
        return result, int(overflow > 0)

    @set_value
    def sbx(self, state, b, a):
        state.cycles += 3
        overflow, result = divmod(b - a + state.registers["EX"], self.cells)
        return result, overflow and 0xffff

    def sti(self, state, b, a):
        state.cycles += 2
        b.set(a.get())
        state.registers["I"] += 1
        state.registers["J"] += 1

    def std(self, state, b, a):
        state.cycles += 2
        b.set(a.get())
        state.registers["I"] -= 1
        state.registers["J"] -= 1

    # a dict of nonbasic opcode numbers to mnemonics
    special_operations = {
        0x01: "jsr", 0x08: "int", 0x09: "iag", 0x0a: "ias", 0x0b: "rfi",
        0x0c: "iaq", 0x10: "hwn", 0x11: "hwq", 0x12: "hwi",
    }

    def special(self, state, o, a):
        "Pass special opcodes to their methods."
        mnemonic = self.special_operations.get(o)
        if mnemonic is None:
            raise OpcodeError(o, state.registers["PC"])
        method = getattr(self, mnemonic)
        return method(state, a)

    def jsr(self, state, a):
        state.cycles += 3
        state.push(state.registers["PC"])
        state.registers["PC"] = a.get()

    def iag(self, state, a):
        state.cycles += 1
        a.set(state.registers["IA"])

    def ias(self, state, a):
        state.cycles += 1
        state.registers["IA"] = a.get()

    def int(self, state, a):
        state.cycles += 4
        "Triggers software interrupt with message A."
        state.interrupt(a.get())

    def rfi(self, state, a):
        state.cycles += 3
        state.queuing = False
        state.registers["A"] = state.pop()
        state.registers["PC"] = state.pop()

    def iaq(self, state, a):
        state.cycles += 2
        state.queuing = bool(a.get())

    def hwn(self, state, a):
        state.cycles += 2
        a.set(len(self.hardware) % self.cells)

    def hwq(self, state, a_value):
        """ From the docs:
        > sets A, B, C, X, Y registers to information about hardware a
        > A+(B<<16) is a 32 bit word identifying the hardware id C is the
        > hardware version X+(Y<<16) is a 32 bit word identifying the
        > manufacturer
        """
        state.cycles += 4
        a = a_value.get()
        if a < len(self.hardware):
            device = self.hardware[a]
            id_top, id_bottom = divmod(device.identifier, self.cells)
            state.registers["B"] = id_top
            state.registers["A"] = id_bottom
            # set C to version
            state.registers["C"] = device.version % self.cells
            m_top, m_bottom = divmod(device.manufacturer, self.cells)
            state.registers["Y"] = m_top
            state.registers["X"] = m_bottom

    def hwi(self, state, a_value):
        state.cycles += 4
        a = a_value.get()
        if a < len(self.hardware):
            state.interrupts.append(a)
