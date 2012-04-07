# -*- coding: utf-8 -*-

import re
from sixteen.dcpu16 import DCPU16
from sixteen.words import from_opcode
from ast import literal_eval


class _meta_parser(type):
    """A metaclass that collects all the @parse methods into a list of pairs
    named __parse_methods__; we'll use this for Parsers.
    
    It also adds all of the @preprocess-ed methods and adds them to
    self.__preprocessors__.
    """
    def __new__(cls, name, bases, dictionary):
        __parse_methods__ = []
        __preprocessors__ = []
        for k, v in dictionary.iteritems():
            if getattr(v, "pattern", None):
                __parse_methods__.append((v.pattern, v))
            if getattr(v, "is_a_preprocessor", None):
                __preprocessors__.append(v)
        dictionary["__parse_methods__"] = __parse_methods__
        dictionary["__preprocessors__"] = __preprocessors__
        return type(name, bases, dictionary)


def parse(pattern):
    """Given a pattern to use as a regular expression, return a decorator that
    sets that function's "pattern" attribute to that pattern.
    """
    def parser_decorator(fn):
        fn.pattern = pattern
        return fn
    return parser_decorator

def preprocess(fn):
    "A decorator that marks this method as a preprocessor."
    fn.is_a_preprocessor = True
    return fn


class Parser(object):
    "A base class for parsers."
    __metaclass__ = _meta_parser

    def parse(self, token):
        """Run all of the preprocessors on the input and check all of the
        __parse_methods__ for a parser that matches this.
        """
        for pattern, method in self.__parse_methods__:
            for pre in self.__preprocessors__:
                token = pre(self, token)
            m = re.match(pattern, token)
            if m:
                return method(self, *m.groups())
        else:
            raise ParserError(token)


class ParserError(Exception):
    "Oh no, we don't know how to parse this thing."


class ValueParser(Parser):
    """Parse values. Values all return a value code and one other thing. The
    one other thing can either be the next word they need or None.
    """
    __metaclass__ = _meta_parser

    registers = ["A", "B", "C", "X", "Y", "Z", "I", "J"]
    rs = r"([a-cx-zijA-CX-ZIJ]{1})"

    # values: all values return their value code and None or their next word
    @parse(r"^%s$" % rs)
    def register(self, name):
        n = self.registers.index(name.upper())
        return n, None

    @parse(r"\[%s\]" % rs)
    def register_pointer(self, name):
        n = self.registers.index(name.upper())
        return 0x08 + n, None

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

    @parse(r"^([a-z]+)$")
    def label(self, l):
        # labels get passed through, to be dealt with later.
        return 0x1f, l


class AssemblyParser(Parser):
    "Parse opcodes and instructions."
    # why doesn't this get inherited from Parser?
    __metaclass__ = _meta_parser
    
    cpu = DCPU16
    opcodes = dict((v, k) for k, v in cpu.opcodes.iteritems())
    special_opcodes = dict((v, k) for k, v in cpu.special_opcodes.iteritems())

    @preprocess
    def comments(self, inp):
        return re.sub(r";.*", "", inp)
     
    @preprocess
    def whitespace(self, inp):
        "Any whitespace leading, trailing, or more than one is insignificant."
        inp = re.sub(r"^\s+", "", inp)
        inp = re.sub(r"\s+$", "", inp)
        return re.sub(r"\s{2,}", " ", inp)

    def __init__(self):
        self.values = ValueParser()

    @parse(r"^\s*$")
    def ignore(self):
        return None,

    def opcode(self, op):
        "Look up an opcode."
        return self.opcodes[op.upper()]

    def special_opcode(self, op):
        "Look up a special opcode."
        return self.special_opcodes[op.upper()]

    # ordinary instructions
    @parse("^(\S+) (\S+?)\,? (\S+)$")
    def instruction(self, op, a, b):
        # get the value codes and extra words for each argument
        a, first_word = self.values.parse(a)
        b, second_word = self.values.parse(b)
        # filter out Nones
        not_nones = tuple(n for n in (first_word, second_word) if n != None)
        # and then put them back at the end
        nones = tuple(None for _ in range(2 - len(not_nones)))
        return (self.opcode(op), a, b) + not_nones + nones

    # special instructions
    @parse("^(\S+?),? (\S+?)$")
    def nonbasic_instructions(self, op, a):
        a, first_word = self.values.parse(a)
        return (0x0, self.special_opcode(op), a, first_word, None)

    def parse_to_ints(self, line):
        parsed = self.parse(line)
        filtered = [p for p in parsed if p != None]
        if len(filtered) >= 3:
            word = from_opcode(*filtered[:3])
            return [word] + filtered[3:]
        else:
            return []

    def parse_iterable(self, iterable):
        "Given an iterable of assembly code, parse each line."
        # TODO: recognize labels, remember them, and interpolate them.
        code = []
        for line in iterable:
            code.extend(self.parse_to_ints(line))
        return list(code)
