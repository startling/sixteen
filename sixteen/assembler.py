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

@ValueParser.register(r"(\S+)")
def label(self, l):
    if l.upper() in self.registers:
        raise Defer()
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
            raise Defer()
        else:
            return gotten

    def parse_iterable(self, iterable):
        "Given an iterable of assembly code, parse each line."
        labels = {}
        code = []
        for line in iterable:
            label, instruction = self.labelled_or_not_instruction(line)
            # if we got a label, remember that label and the address
            if label != None:
                labels[label] = len(code)
            if instruction != None:
                code.extend(self.parse(instruction))
        # get all the labels that the value parser has seen but that aren't
        # defined in the code.
        undefined_labels = [l for l in self.values.labels if l not in labels]
        # if there are any, raise an error.
        if len(undefined_labels) > 0:
            raise LabelError(undefined_labels)
        # and then pass through the code again, replacing labels with addresses
        final = []
        for word in code:
            gotten = labels.get(word)
            if gotten == None:
                final.append(word)
            else:
                final.append(gotten)
        #TODO: short labels
        return final


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
    return ()


# special instructions
@AssemblyParser.register("^(\S+?),? (.+)$")
def nonbasic_instructions(self, op, a):
    # parse the opcode first, so it Defers right of the bat if this is an
    # illegal opcode
    o = self.special_opcode(op)
    a, first_word = self.values.parse(a)
    if first_word == None:
        return (from_opcode(0x0, o, a,),)
    else:
        return (from_opcode(0x0, o, a,), first_word)


# ordinary instructions
@AssemblyParser.register("^(\S+) ([^,]+)\,? (.+)$")
def instruction(self, op, a, b):
    # parse the opcode first, so it Defers right of the bat if this is an
    # illegal opcode
    o = self.opcode(op)
    # get the value codes and extra words for each argument
    a, first_word = self.values.parse(a)
    b, second_word = self.values.parse(b)
    # filter out Nones
    not_nones = tuple(n for n in (first_word, second_word) if n != None)
    return (from_opcode(o, a, b),) + not_nones


@AssemblyParser.register("^(dat|DAT|.dat) (([^ ,]+,?\s?)+)$")
def dat(self, name, words, _):
    given = (w for w in re.split(r"\s|,", words) if w)
    data = []
    for d in given:
        try:
            data.append(self.values.literal(d, both=False))
        except Defer:
            # otherwise, its a label.
            data.append(d)
    return data

        
@AssemblyParser.register("^(jmp|JMP) (.+)$")
def jmp(self, _, address):
    return self.instruction("set pc, %s" % address)


class LabelError(Exception):
    def __init__(self, values):
        self.values = values

    def __str__(self):
        if len(self.values) == 1:
            return "%r is an undefined label." % self.values[0]
        else:
            return "%s are undefined labels." % ", ".join(self.values)
