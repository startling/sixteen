# -*- coding: utf-8 -*-

from functools import wraps


class Value(object):
    def __init__(self, registers, cpu, iterator):
        """Values get initialized with three things: 
         * a dictionary of the cpu's registers
         * a list of the values in the cpu's ram
         * an iterator over the ram
        
        It shouldn't touch any of these except, optionally, the iterator. NO
        SIDE EFFECTS!! The cpu will see what's been done to the iterator and
        then decide what to do.
        """
        self.registers = registers
        self.cpu = cpu
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


class NextWordPointer(Consumes):
    def get(self):
        return self.ram[self.value]

    def set(self, value):
        return {}, {self.value: value}
