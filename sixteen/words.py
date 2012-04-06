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


def from_hex(word):
    return int(word, base=16)


def as_opcode(word):
    """Interpret this word as an opcode. from the docs:

    'a basic instruction has the format: bbbbbbaaaaaaoooo'

    This method returns three integers: o, a, and b.
    """
    # mask away everything but the opcode
    o = word & 0b0000000000001111
    # shift away the opcode
    a_and_b = word >> 4
    # mask away b to get a
    a = a_and_b & 0b000000111111
    # shift away a to get b
    b = a_and_b >> 6
    return o, a, b


def from_opcode(o, a, b):
    """Given o, a, and b as integers, return an integer such that its binary
    representation looks like 'bbbbbbaaaaaaoooo'.
    """
    # o is the least significant, so it doesn't get shifted at all
    # a gets shifted left by four, because o is four bits long.
    # b gets shifted left by ten, because o is four bits and a is six.
    return o ^ (a << 4) ^ (b << 10)
