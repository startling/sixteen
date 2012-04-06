# -*- coding: utf-8 -*-

from functools import wraps


class Box(object):
    """A base class that defines the Box interface with some sane defaults.
    Everything that will be used as a box *needs* these three methods: "get",
    "set", and, of course, "__init__".

    Each Box's __init__ takes two arguments -- "self", of course, and "cpu",
    which is probably an instance of sixteen.dcpu16.DCPU16. The default thing
    to do is to save "key"and "container" attributes, which are used to look up
    or set things in "get" and "set".

    There's also a `consumed` attribute that starts at None and should be set
    to an int if the Box gets a new word. There's also a @consume decorator
    (scroll down a bit) that sets it and passes it to the "__init__".

    And then there's the "dis" attribute that should be a human-readable string
    ("disassembled") for this value.

    This class (it *is* a base class) doesn't define "__init__", so you'll need
    to subclass and define it yourself.
    """
    consumed = None

    def get(self):
        """'get' is called to retrieve the contained value. Nothing
        destructive should happen here. Everything that gets the next word etc
        should happen in __init__.
        """
        return self.container[self.key]

    def set(self, value):
        "This is what gets called when something tries to change this value."
        self.container[self.key] = value


def consume(fn):
    @wraps(fn)
    def initialize(self, cpu):
        self.consumed = cpu.get_next()
        fn(self, cpu, self.consumed)
    return initialize


class Register(object):
    """This class abstracts away much of the work for registers. It isn't a Box
    subclass itself, but it defines three methods that construct and return
    such classes. 
    """
    def __init__(self, name):
        "Given the name of this register, initialize a Register."
        self.name = name

    def as_value(self):
        "Return a Box that gets and sets the value of this register."
        def value_init(s, cpu):
            s.container = cpu.registers

        value = type(self.name, (Box,),
                {"__init__": value_init, "dis": self.name})
        value.key = self.name
        return value

    def as_pointer(self):
        "Return a Box that gets and sets the value this register points to."
        def pointer_init(s, cpu):
            s.container = cpu.RAM
            s.key = cpu.registers[self.name]

        return type("[%s]" % self.name, (Box,),
            {"__init__": pointer_init, "dis": "[%s]" % self.name})

    def and_next_word(self):
        """Return a box that gets and sets the register the sum of this
        register and the next word points to.
        """
        @consume
        def r_init(s, cpu, next_word):
            s.container = cpu.RAM
            s.key = cpu.registers[self.name] + next_word
            s.dis = "[0x%04x + %s]" % (next_word, self.name)
            # handle overflow
            if s.key >= len(cpu.RAM) - 1:
                s.key -= (cput.RAM - 1)

        return type("[%s + next word]" % self.name, (Box,),
                {"__init__": r_init})


class NextWord(Box):
    "0x1f: next word (literal)"
    @consume
    def __init__(self, cpu, next_word):
        self.value = next_word
        self.dis = "0x%04x" % next_word
    
    def get(self):
        return self.value

    def set(self, value):
        """"So say the docs:
        'If any instruction tries to assign a literal value, the assignment fails
        silently. Other than that, the instruction behaves as normal.'
        """
        # AMBIGUITY: does that apply to next word literals, or just short form
        # literals?
        pass
    

class NextWordAsPointer(Box):
    "0x1e: [next word]"
    @consume
    def __init__(self, cpu, next_word):
        "Get and set to and from the address stored in the next word."
        self.container = cpu.RAM
        self.key = next_word
        self.dis = "[0x%04x]" % next_word


def ShortLiteral(n):
    "0x20-0x3f: literal value 0x00-0x1f (literal)"
    class LiteralN(Box):
        def __init__(self, cpu):
            self.value = n
            self.dis = "0x%04x" % n
        
        def get(self):
            return self.value

        def set(self, value):
            """"So say the docs:
            'If any instruction tries to assign a literal value, the assignment fails
            silently. Other than that, the instruction behaves as normal.'
            """
            pass

    return LiteralN


class PUSH(Box):
    "0x1a: PUSH / [--SP]"
    dis = "PUSH"

    def __init__(self, cpu):
        "Decrement the counter and point to the address in SP."
        self.container = cpu.RAM
        cpu.registers["SP"] -= 1
        # handle underflow
        if cpu.registers["SP"] < 0:
            cpu.registers["SP"] = len(cpu.RAM) - 1
        self.key = cpu.registers["SP"]


class POP(Box):
    "0x18: POP / [SP++]"
    dis = "POP"

    def __init__(self, cpu):
        "Save the value at the pointer for later and increment the counter."
        self.container = cpu.RAM
        self.key = cpu.registers["SP"]
        self.value = self.container[self.key]
        cpu.registers["SP"] += 1
        # handle overflow
        if cpu.registers["SP"] == len(cpu.RAM) - 1:
            cpu.registers["SP"] = 0x0000
        # AMBIGUITY: does SET POP, A set to the place where the popped value
        # came from, or the new place where SP points?
    
    def get(self):
        return self.value
