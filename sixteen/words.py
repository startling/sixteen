# -*- coding: utf-8 -*-

from bitstring import Bits


class Word(object):
    """These objects represent DCPU-16 words, and they can be interpreted
    either as opcodes or as literals.
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
