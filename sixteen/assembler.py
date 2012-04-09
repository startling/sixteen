# -*- coding: utf-8 -*-

import re
from ast import literal_eval
from sixteen.words import from_opcode
from sixteen.parser import Parser, Defer
from sixteen.dcpu16 import DCPU16


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


@ValueParser.register(r"\[([^+ ]+)\s?\+\s?([^+ ])\]")
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


class AssemblyParser(Parser):
    cpu = DCPU16
    opcodes = dict((v, k) for k, v in cpu.opcodes.iteritems())
    special_opcodes = dict((v, k) for k, v in cpu.special_opcodes.iteritems())

    def __init__(self):
        self.values = ValueParser()

    def labelled_or_not_instruction(self, instruction):
        """Extract a label definition from an instruction, if it's there;
        return that (or None) and the newly-unlabeled instruction.
        """
        m = re.match(r"^\s*(:(\w+))?\s*(.*)$", instruction)
        if m:
            return m.group(2), m.group(3) or None
        else:
            return None, instruction

    def opcode(self, op):
        "Look up an opcode."
        gotten = self.opcodes.get(op.upper())
        if gotten == None:
            raise Defer()
        else:
            return gotten

    def special_opcode(self, op):
        "Look up a special opcode."
        gotten = self.special_opcodes.get(op.upper())
        if gotten == None:
            raise OpcodeError(op)
        else:
            return gotten

    def parse_to_ints(self, line):
        parsed = self.parse(line)
        filtered = [p for p in parsed if p != None]
        if len(filtered) >= 3:
            word = from_opcode(*filtered[:3])
            return [word] + filtered[3:]
        else:
            return []

@AssemblyParser.preprocess
def comments(self, inp):
    "Remove comments and the whitespace up to them."
    return re.sub(r"\s*;.*", "", inp)

@AssemblyParser.preprocess
def whitespace(self, inp):
    "Any whitespace leading, trailing, or more than one is insignificant."
    inp = re.sub(r"^\s+", "", inp)
    inp = re.sub(r"\s+$", "", inp)
    return re.sub(r"\s{2,}", " ", inp)


@AssemblyParser.register(r"^\s*$")
def ignore(self):
    return None,


# special instructions
# (that horrible regex for the second argument is to allow spaces only
# inside of brackets with a +; this way, things stay unambiguous between
# ordinary and non-basic instructions, yet there can still be spaces inside
# brackets.)
@AssemblyParser.register("^(\S+?),? (\S+|\[\S+\s\+\s\S+\])$")
def nonbasic_instructions(self, op, a):
    a, first_word = self.values.parse(a)
    return (0x0, self.special_opcode(op), a, first_word, None)

# ordinary instructions
@AssemblyParser.register("^(\S+) ([^,]+)\,? (.+)$")
def instruction(self, op, a, b):
    # get the value codes and extra words for each argument
    a, first_word = self.values.parse(a)
    b, second_word = self.values.parse(b)
    # filter out Nones
    not_nones = tuple(n for n in (first_word, second_word) if n != None)
    # and then put them back at the end
    nones = tuple(None for _ in range(2 - len(not_nones)))
    return (self.opcode(op), a, b) + not_nones + nones

