# -*- coding: utf-8 -*-

import re
from sixteen.dcpu16 import DCPU16
from sixteen.words import from_opcode
from ast import literal_eval


class _meta_parser(type):
    """A metaclass that collects all the @parse methods into a list of pairs
    named __parse_methods__; we'll use this for Parsers.
    """
    def __new__(cls, name, bases, dictionary):
        __parse_methods__ = []
        for k, v in dictionary.iteritems():
            if getattr(v, "pattern", None):
                __parse_methods__.append((v.pattern, v))
        dictionary["__parse_methods__"] = __parse_methods__
        return type(name, bases, dictionary)


def parse(pattern):
    """Given a pattern to use as a regular expression, return a decorator that
    sets that function's "pattern" attribute to that pattern.
    """
    def parser_decorator(fn):
        fn.pattern = pattern
        return fn
    return parser_decorator


class Parser(object):
    "A base class for parsers."
    __metaclass__ = _meta_parser

    def parse(self, token):
        "Check all of the __parse_methods__ for a parser that matches this."
        for pattern, method in self.__parse_methods__:
            m = re.match(pattern, token)
            if m:
                return method(self, *m.groups())
        else:
            # oh no, nothing matched.
            return False


class AssemblyParser(Parser):
    # why doesn't this get inherited from Parser?
    __metaclass__ = _meta_parser
    
    cpu = DCPU16
    opcodes = dict((v, k) for k, v in cpu.opcodes.iteritems())

    registers = ["A", "B", "C", "X", "Y", "Z", "I", "J"]
    rs = r"([a-cx-zijA-CX-ZIJ]{1})"

    # values: all values return their value code and None or their next word
    @parse(r"^%s$" % rs)
    def register(self, name):
        n = self.registers.index(name.upper())
        return (n, None)

    @parse(r"\[%s\]" % rs)
    def register_pointer(self, name):
        n = self.registers.index(name.upper())
        return (0x08 + n, None)

    @parse(r"\[(.+)\s?\+\s?%s\]" % rs)
    def register_plus_next_word(self, num, reg):
        code = 0x10 + self.registers.index(reg.upper())
        return code, literal_eval(num)

    @parse(r"\[SP\+\+\]|POP")
    def POP(self):
        return 0x18, None

    @parse(r"\[SP\]|PEEK")
    def PEEK(self):
        return 0x19, None

    @parse(r"\[--SP\]|PUSH")
    def POP(self):
        return 0x1a, None

    @parse("SP")
    def SP(self):
        return 0x1b, None

    @parse("PC")
    def PC(self):
        return 0x1c, None

    @parse("O")
    def O(self):
        return 0x1d, None

    @parse(r"\[([^+]+)\]")
    def next_word_pointer(self, num):
        return 0x1e, literal_eval(num)

    @parse(r"^(0x[0-9a-fA-F]+|0b[01]+|0o[0-7]+|[0-9]+)$")
    def literal(self, num):
        num = literal_eval(num)
        if num <= 0x1f:
            return 0x20 + num, None
        else:
            return 0x1f, num

    @parse(r"^(:\S+)")
    def label(self, l):
        # labels get passed through, to be dealt with later.
        return 0x1f, l

    @parse("^(%s)$" % "|".join(opcodes.keys()))
    def opcode(self, code):
        return self.opcodes[code]

    @parse(r"^\s*(;.*)?$")
    def ignore(self, _):
        return None,

    # ordinary instructions
    @parse("\s*([^\[\] \t\n]+) (\S+?)\,? ([^; \t\n]+)\s*;?.*$")
    def instruction(self, op, a, b):
        # get the value codes and extra words for each argument
        a, first_word = self.parse(a)
        b, second_word = self.parse(b)
        # filter out Nones
        not_nones = tuple(n for n in (first_word, second_word) if n != None)
        # and then put them back at the end
        nones = tuple(None for _ in range(2 - len(not_nones)))
        return (self.parse(op), a, b) + not_nones + nones


    def parse_to_ints(self, line):
        parsed = self.parse(line)
        filtered = [p for p in parsed if p != None]
        if len(filtered) >= 3:
            word = from_opcode(*filtered[:3])
            return [word] + filtered[3:]
        else:
            return []
