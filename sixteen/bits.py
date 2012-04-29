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

from math import log


def from_hex(word):
    return int(word, base=16)


def as_instruction(word):
    """Interpret this word as an opcode. from the docs:

    > In bits (in LSB-0 format), a basic instruction has the format:
    > aaaaaabbbbbooooo.

    This method returns three integers: o, a, and b.
    """
    # mask away everything but the opcode
    o = word & 0b0000000000011111
    # shift away the opcode
    a_and_b = word >> 5
    # mask away a to get b
    b = a_and_b & 0b000000011111
    # shift away b to get a
    a = a_and_b >> 5
    return o, b, a


def from_instruction(o, b, a):
    """Given o, b, and a as integers, return an integer such that its binary
    representation looks like 'aaaaaabbbbbooooo'.
    """
    # raise an error if we get a `b` that would take more than five bits.
    if b > 31:
        raise ValueError("`b` can only be five bits long, got {0:b}.".format(a))
    # o is the least significant, so it doesn't get shifted at all
    # b gets shifted left by five, because o is five bits long.
    # a gets shifted left by ten, because o is five bits and a is five.
    return o ^ (b << 5) ^ (a << 10)


def bit_iter(bits, n):
    "Iterate over the bits of an integer, padding it to `n` digits."
    return ((bits >> i) & 1 for i in xrange(n - 1, -1, -1))


def invert(i, n):
    "Calculate the inverse of an n-bit long integer, i."
    return i ^ (2 ** n - 1)


def as_signed(i):
    "Interpret this integer as signed (two's complement)."
    return -(invert(i, 16) + 1) if i >> 15 else i


def from_signed(i):
    "Turn this signed integer into a two's complement (unsigned) integer."
    return i if i >= 0 else invert(abs(i), 16) + 1
