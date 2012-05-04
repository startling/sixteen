# -*- coding: utf-8 -*-

from sixteen.dcpu16 import DCPU16
from sixteen.utilities import OpcodeError


def disassembler(cpu=None):
    "An iterator that disassembles."
    cpu = cpu or DCPU16()
    n = 0
    while any(cpu.ram[n:]):
        _, _, state = cpu.get_instruction(n)
        yield state.dis, n
        n = state.registers["PC"]
