# -*- coding: utf-8 -*-

from itertools import permutations
from sixteen.dis import Disassembler


def fuzzer(words):
    "Generate and yield every possible program up to a given amount of words."
    for code in permutations(xrange(0x10000), words):
        # disassemble the code
        d = Disassembler()
        d[:words] = code
        dis = " / ".join(o for o, _ in d.dis())
        yield code, dis
