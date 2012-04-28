# -*- coding: utf-8 -*-


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

    def __init__(self):
        # make a dictionary of all the registers of this class, initializing
        # them all to 0x0000.
        self.registers = dict((r, 0x0000) for r in self._registers)

    def cycle(self):
        "Run for one instruction, returning the executed instruction."
        pass

    def __getattr__(self, name):
        "If an attribute doesn't exist, try the registers."
        r = self.registers.get(name.upper())
        if r == None:
            raise AttributeError(name)
        else:
            return r
