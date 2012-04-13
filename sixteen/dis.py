# -*- coding: utf-8 -*-

from sixteen.dcpu16 import DCPU16
from sixteen.utilities import OpcodeError


class Disassembler(DCPU16):
    "A subclass of the DCPU16 that disassembles."
    def dis(self):
        "Return an iterator over the code in memory, yielding it disassembled."
        # until the rest of the RAM is 0x0000
        while any(self.RAM[self.registers["PC"]:]):
            address = self.registers["PC"]
            next_word = self.get_next()
            try:
                # parse the opcodes and values out of the next word
                opcode, values = self.parse_instruction(next_word)
                # print each opcode and its arguments
                assembly = "%s %s" % (opcode, ", ".join([v.dis for v in values]))
            # if there's an OpcodeError, it's a DAT instruction.
            except OpcodeError:
                assembly = "DAT 0x%04x" % next_word
            yield assembly, address
