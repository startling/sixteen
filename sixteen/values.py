# -*- coding: utf-8 -*-

from functools import wraps


class Value(object):
    def __init__(self, state, is_a):
        """Values get initialized with a state object, whose attributes it can
        safely modify.
        """
        self.state = state
        self.registers = state.registers
        self.ram = state.ram
        self.is_a = is_a
        self.is_b = not is_a

    def set(self, value):
        """This should update self.registers or self.ram."""
        pass

    def get(self):
        "This should return whatever value that should be gotten."
        raise NotImplementedError()


class Consumes(Value):
    "A type of value that consumes a value from RAM on initialization."
    def __init__(self, state, is_a):
        Value.__init__(self, state, is_a)
        self.value = next(state.ram_iter)
        state.cycles += 1


class NextWord(Consumes):
    def get(self):
        return self.value

    # setting to next word literals is silently ignored.

    @property
    def dis(self):
        return "0x%04x" % self.value


class NextWordPointer(Consumes):
    def get(self):
        return self.ram[self.value]

    def set(self, value):
        self.ram[self.value] = value

    @property
    def dis(self):
        return "[0x%04x]" % self.value


class Register(Value):
    """A base class for register values. Create a new class for a register with
    `Myclass.named("PC")`, substituting the name of the register in.
    """
    @classmethod
    def named(cls, name):
        return type(name, (cls,), {"name": name})


class RegisterValue(Register):
    "A register's value."
    def get(self):
        return self.registers[self.name]

    def set(self, value):
        self.registers[self.name] = value

    @property
    def dis(self):
        return self.name


class RegisterPointer(Register):
    "A register's value as a pointer."
    def get(self):
        return self.ram[self.registers[self.name]]

    def set(self, value):
        self.ram[self.registers[self.name]] = value

    @property
    def dis(self):
        return "[%s]" % self.name


class RegisterPlusNextWord(Register, Consumes):
    "The value of a register and the next word as a pointer."
    def get(self):
        return self.ram[self.registers[self.name] + self.value]

    def set(self, value):
        self.ram[self.registers[self.name] + self.value] = value

    @property
    def dis(self):
        return "[%s + 0x%04x]" % (self.name, self.value)


def Literal(n):
    return type(hex(n), (Value,), {
        "get": lambda self: n,
        "dis": "0x%04x" % n
    })


def POPorPUSH(state, is_a):
    if is_a:
        return POP(state, is_a)
    else:
        return PUSH(state, is_a)


class POP(Register):
    dis = "POP"

    def __init__(self, *args):
        Register.__init__(self, *args)
        self.value = self.state.pop()

    def get(self):
        return self.value


class PUSH(Register):
    dis = "PUSH"

    def __init__(self, *args):
        Register.__init__(self, *args)
        self.state.registers["SP"] -= 1
        self.state.registers["SP"] %= 0x10000
        self.location = self.state.registers["SP"]

    def get(self):
        return self.state.ram[self.location]

    def set(self, value):
        self.state.ram[self.location] = value
