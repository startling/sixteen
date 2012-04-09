# -*- coding: utf-8 -*-

from sixteen.parser import Parser, Defer
from ast import literal_eval


class ValueParser(Parser):
    """Parse values. Values all return a value code and one other thing. The
    one other thing can either be the next word they need or None.
    """
    registers = ["A", "B", "C", "X", "Y", "Z", "I", "J"]
    def __init__(self):
        # a set to store all the labels we've seen
        self.labels = set()


@ValueParser.register("SP|sp")
def sp(self):
    return 0x1b, None


@ValueParser.register("(\S+)")
def register(self, r):
    try:
        return self.registers.index(r.upper()), None
    except ValueError:
        raise Defer()


@ValueParser.register(r"\[(\S+)\]")
def register_pointer(self, name):
    try:
        return self.registers.index(name.upper()) + 0x08, None
    except ValueError:
        raise Defer()


@ValueParser.register(r"\[(.+) \+ (.+)]")
def register_plus_next_word(self, num, reg):
    try:
        code = 0x10 + self.registers.index(reg.upper())
        return code, self.literal(num, both=False)
    except ValueError:
        Defer()


@ValueParser.register(r"\[SP\+\+\]|POP|pop|\[sp\+\+\]")
def POP(self):
    return 0x18, None


@ValueParser.register(r"\[SP\]|PEEK|\[sp\]|peek")
def PEEK(self):
    return 0x19, None


@ValueParser.register(r"\[--SP\]|PUSH|\[--sp\]|push")
def PUSH(self):
    return 0x1a, None


@ValueParser.register("SP|sp")
def SP(self):
    return 0x1b, None


@ValueParser.register("PC|pc")
def PC(self):
    return 0x1c, None


@ValueParser.register("O|o")
def O(self):
    return 0x1d, None


@ValueParser.register(r"\[(.+)\]")
def next_word_pointer(self, num):
    return 0x1e, self.literal(num, both=False)


@ValueParser.register(r"^([-+]?)(0x[0-9a-fA-F]+|0b[01]+|0o[0-7]+|[0-9]+)$")
def literal(self, sign, n, both=True):
    num = literal_eval(n)
    if sign == "-" and num != 0:
        num = 0x10000 - num
    if num > 0xffff:
        raise Defer()
    if both:
        if num <= 0x1f:
            return 0x20 + num, None
        else:
            return 0x1f, num
    else:
        return num

@ValueParser.register(r"([a-zA-Z_]+)")
def label(self, l):
    self.labels.add(l)
    # labels get passed through, to be dealt with later.
    return 0x1f, l
