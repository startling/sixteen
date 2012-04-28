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

    def cycle(self):
        "Run for one instruction, returning the executed instruction."
        pass

    def ram_iter(self):
        """Return an iterator over this cpu's RAM and a list that will be updated
        whenever a value is drawn.
        """
        consumed = []
        def i():
            place = self.ram["pc"]
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
