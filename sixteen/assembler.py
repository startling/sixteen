# -*- coding: utf-8 -*-

import re
from ast import literal_eval
from itertools import chain
from sixteen.bits import from_instruction
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


@ValueParser.pattern("^SP|sp$")
def sp(self):
    return 0x1b, None


@ValueParser.pattern("^(\S+)$")
def register(self, r):
    try:
        return self.registers.index(r.upper()), None
    except ValueError:
        raise Defer()


@ValueParser.pattern(r"^\[(\S+)\]$")
def register_pointer(self, name):
    try:
        return self.registers.index(name.upper()) + 0x08, None
    except ValueError:
        raise Defer()


@ValueParser.pattern(r"^\[([^+ ]+)\s?\+\s?([^+ ])\]$")
def register_plus_next_word(self, num, reg):
    try:
        code = 0x10 + self.registers.index(reg.upper())
        return code, self.literal(num, both=False)
    except ValueError:
        raise Defer()


@ValueParser.pattern(r"^\[SP\+\+\]|POP|pop|\[sp\+\+\]$")
def POP(self):
    return 0x18, None


@ValueParser.pattern(r"^\[SP\]|PEEK|\[sp\]|peek$")
def PEEK(self):
    return 0x19, None


@ValueParser.pattern(r"^\[--SP\]|PUSH|\[--sp\]|push$")
def PUSH(self):
    return 0x1a, None


@ValueParser.pattern("^SP|sp$")
def SP(self):
    return 0x1b, None


@ValueParser.pattern("^PC|pc$")
def PC(self):
    return 0x1c, None


@ValueParser.pattern("^EX|ex$")
def EX(self):
    return 0x1d, None


@ValueParser.pattern(r"^\[(.+)\]$")
def next_word_pointer(self, num):
    return 0x1e, self.literal(num, both=False)


@ValueParser.pattern(r"^([-+]?)(0x[0-9a-fA-F]+|0b[01]+|0o[0-7]+|[0-9]+)$")
def literal(self, sign, n, both=True):
    num = literal_eval(n)
    if sign == "-" and num != 0:
        num = 0x10000 - num
    if num > 0xffff:
        raise Defer()
    if both:
        if num <= 0x1f:
            return 0x21 + num, None
        elif num == 0xffff:
            return 0x20, None
        else:
            return 0x1f, num
    else:
        return num


@ValueParser.pattern(r"^\[(\S+)\s?\+\s?(\S+)\]$")
def label_plus_register_pointer(self, label, register):
    if label.upper() in self.registers:
        raise Defer()
    if register.upper() not in self.registers:
        raise Defer()
    self.labels.add(label)
    index = self.registers.index(register.upper())
    return index + 0x10, label


@ValueParser.pattern(r"^\[(\S+)\]$")
def label_pointer(self, l):
    if l.upper() in self.registers:
        raise Defer()
    self.labels.add(l)
    return 0x1e, l

@ValueParser.pattern(r"^(\S+)$")
def label(self, l):
    if l.upper() in self.registers:
        raise Defer()
    self.labels.add(l)
    # labels get passed through, to be dealt with later.
    return 0x1f, l


class AssemblyParser(Parser):
    cpu = DCPU16
    opcodes = dict((v, k) for k, v in cpu.operations.iteritems())
    special_opcodes = dict((v, k)
            for k, v in cpu.special_operations.iteritems())

    def __init__(self):
        self.values = ValueParser()
        self.labels = []

    def opcode(self, op):
        "Look up an opcode."
        gotten = self.opcodes.get(op.upper()) or self.opcodes.get(op.lower())
        if gotten == None:
            raise Defer()
        else:
            return gotten

    def special_opcode(self, op):
        "Look up a special opcode."
        gotten = (self.special_opcodes.get(op.upper()) or
                self.special_opcodes.get(op.lower()))
        if gotten == None:
            raise Defer()
        else:
            return gotten


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


@AssemblyParser.pattern(r"^\s*$")
def ignore(self):
    return []


# label definitions
@AssemblyParser.pattern(r"^:(\w+)\s*(.*)$")
def label_definition(self, label, instruction):
    if label in (l for l, _ in self.labels):
        raise MultipleLabelDefs(label)
    parsed = self.parse(instruction)
    self.labels.append((label, parsed,))
    return parsed


# special instructions
@AssemblyParser.pattern("^(\S+?)(?:,|\s)\s?(.+)$")
def nonbasic_instructions(self, op, a):
    # parse the opcode first, so it Defers right of the bat if this is an
    # illegal opcode
    o = self.special_opcode(op)
    a, first_word = self.values.parse(a)
    if first_word == None:
        return [from_instruction(0x0, o, a,)]
    else:
        return [from_instruction(0x0, o, a,), first_word]


# ordinary instructions
@AssemblyParser.pattern("^(\S+) ([^,]+)(?:,|\s)\s?(.+)$")
def instruction(self, op, b, a):
    # parse the opcode first, so it Defers right of the bat if this is an
    # illegal opcode
    o = self.opcode(op)
    # get the value codes and extra words for each argument
    a, first_word = self.values.parse(a)
    b, second_word = self.values.parse(b)
    # filter out Nones
    not_nones = list(n for n in (first_word, second_word) if n != None)
    return [from_instruction(o, b, a)] + not_nones


def string_literal(literal):
    double_quoted = re.match(r'^"(.+)"$', literal)
    single_quoted = re.match(r"^'(.+)'$", literal)
    if double_quoted:
        unescaped = re.sub(r'\\(.)', r'\1', double_quoted.group(1))
        return [ord(c) for c in unescaped]
    elif single_quoted:
        unescaped = re.sub(r'\\(.)', r'\1', single_quoted.group(1))
        return [ord(c) for c in unescaped]
    else:
        raise Defer()


@AssemblyParser.pattern("^(?:dat|DAT|.dat) ((?:.+,?\s?)+)$")
def dat(self, words):
    given = (w for w in re.split(r"\s|,", words) if w)
    data = []
    for d in given:
        try:
            data.append(self.values.literal(d, both=False))
        except Defer:
            # otherwise, its either a label or a string literal.
            try:
                data.extend(string_literal(d))
            except Defer:
                data.append(d)
    return data

        
@AssemblyParser.pattern("^(?:jmp|JMP) (.+)$")
def jmp(self, address):
    return self.instruction("set pc, %s" % address)


@AssemblyParser.translator
def add_labels(self, tree):
    "Parse the tree and replace labels with addresses."
    # raise an error for undefined labels
    undefined = [l for l in self.values.labels if l not in 
            (x for x, _ in self.labels)]
    if undefined:
        raise UndefinedLabel(undefined)
    # replace all of the labels with their locations
    for l, value in self.labels:
        # first pass -- get the location of the labelled node
        for num, node in enumerate(tree):
            if node is value:
                location = sum(len(_node) for _node in tree[:num])
                break
        else:
            raise LabelError(l)
        # second pass -- replace all instances of that label with the node's
        # location.
        for node in tree:
            for n, word in enumerate(node):
                if word == l:
                    node[n] = location
    return tree


@AssemblyParser.translator
def concatenate(self, tree):
    "Turn all of the nodes into one big list."
    return list(chain(*tree))


class LabelError(Exception):
    pass


class UndefinedLabel(LabelError):
    def __init__(self, values):
        self.values = values

    def __str__(self):
        if len(self.values) == 1:
            return "%r is an undefined label." % self.values[0]
        else:
            return "%s are undefined labels." % ", ".join(self.values)


class MultipleLabelDefs(LabelError):
    def __init__(self, value):
        self.values = value

    def __str__(self):
        return "%r is defined multiple times." % self.values
