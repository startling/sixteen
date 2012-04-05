# -*- coding: utf-8 -*-
"""These functions help represent DCPU-16 words, and they can be interpreted
either as opcodes or as literals.

DCPU-16 words are sixteen-bit unsigned.

From the docs:
> Instructions are 1-3 words long and are fully defined by the first word.  In
> a basic instruction, the lower four bits of the first word of the instruction
> are the opcode, and the remaining twelve bits are split into two six bit
> values, called a and b. a is always handled by the processor before b, and is
> the lower six bits. In bits (with the least significant being last), a basic
> instruction has the format: bbbbbbaaaaaaoooo
"""

from bitstring import Bits


def from_hex(word):
    return int(word, base=16)


def as_opcode(word):
    """Interpret this word as an opcode. from the docs:

    'a basic instruction has the format: bbbbbbaaaaaaoooo'

    This method returns three integers: o, a, and b.
    """
    bitarray = Bits("0x%04x" % word)
    b = bitarray[:6]
    a = bitarray[6:-4]
    o = bitarray[-4:]
    return o.uint, a.uint, b.uint
