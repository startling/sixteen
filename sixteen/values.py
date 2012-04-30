# -*- coding: utf-8 -*-

from functools import wraps


class DeltaDict(object):
    """A dictionary-like object that's initialized with another dictionary.
    Setting to it, though, doesn't mutate the original; instead, those changes
    get put into a new dictionary.
    """
    def __init__(self, original):
        self._original = original
        self.changes = {}

    def __setitem__(self, key, value):
        "Always set to the new dict."
        self.changes[key] = value

    def __getitem__(self, key):
        """Try getting from the new dict; if that fails, try to get it from the
        original.
        """
        return self.changes.get(key) or self.original[key]

    def __iter__(self):
        return iter(self.changes)


class Value(object):
    def __init__(self, registers, ram, iterator):
        """Values get initialized with three things: 
         * a dictionary of the cpu's registers
         * a list of the values in the cpu's ram
         * an iterator over the ram
        
        It shouldn't touch any of these except, optionally, the iterator. NO
        SIDE EFFECTS!! The cpu will see what's been done to the iterator and
        then decide what to do.
        """
        self.registers = registers
        self.ram = ram
        self.iterator = iterator

    def set(self, value):
        """This should return a dictionary to update the registers with and a
        dictionary to update the RAM with.
        """
        return {}, {}

    def get(self):
        "This should return whatever value that should be gotten."
        raise NotImplementedError()


class Consumes(Value):
    "A type of value that consumes a value from RAM on initialization."
    def __init__(self, registers, cpu, iterator):
        Value.__init__(self, registers, cpu, iterator)
        self.value = next(iterator)


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
        return {}, {self.value: value}

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
        return {self.name: value}, {}

    @property
    def dis(self):
        return self.name


class RegisterPointer(Register):
    "A register's value as a pointer."
    def get(self):
        return self.ram[self.registers[self.name]]

    def set(self, value):
        return {}, {self.registers[self.name]: value}

    @property
    def dis(self):
        return "[%s]" % self.name


class RegisterPlusNextWord(Register, Consumes):
    "The value of a register and the next word as a pointer."
    def get(self):
        return self.ram[self.registers[self.name] + self.value]

    def set(self, value):
        return {}, {self.registers[self.name] + self.value: value}

    @property
    def dis(self):
        return "[%s + 0x%04x]" % (self.name, self.value)


def Literal(n):
    return type(hex(n), (Value,), {
        "get": lambda self: n,
        "dis": "0x%04x" % n
    })
