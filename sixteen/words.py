# -*- coding: utf-8 -*-

from bitstring import Bits


class Word(object):
    """These objects represent DCPU-16 words, and they can be interpreted
    either as opcodes or as literals.

    DCPU-16 words are sixteen-bit unsigned.

    From the docs:
    > Instructions are 1-3 words long and are fully defined by the first word.
    > In a basic instruction, the lower four bits of the first word of the
    > instruction are the opcode, and the remaining twelve bits are split into
    > two six bit values, called a and b. a is always handled by the processor
    > before b, and is the lower six bits. In bits (with the least significant
    > being last), a basic instruction has the format: bbbbbbaaaaaaoooo
    """
    def __init__(self, word):
        "Given a Bits or a BitArray, initialize this word."
        self._word = word

    @classmethod
    def from_hex(cls, word):
        "Initialize a Word given a string of hexadecimal."
        return cls(Bits("0x" + word))

    def as_opcode(self):
        """Interpret this word as an opcode. from the docs:

        'a basic instruction has the format: bbbbbbaaaaaaoooo'

        This method returns three integers: o, a, and b.
        """
        b = self._word[:6]
        a = self._word[6:-4]
        o = self._word[-4:]
        return o.uint, a.uint, b.uint
    
    def as_literal(self):
        "Interpret this word as a literal; returns one integer."
        return self._word.uint
