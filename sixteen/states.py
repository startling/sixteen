# -*- coding: utf-8 -*-


class DeltaDict(object):
    """A dictionary-like object that's initialized with another dictionary.
    Setting to it, though, doesn't mutate the original; instead, those changes
    get put into a new dictionary.
    """
    def __init__(self, original):
        self._original = original
        self.changes = {}

    def __setitem__(self, key, value):
        "Always set to the new dict."
        self.changes[key] = value

    def __getitem__(self, key):
        """Try getting from the new dict; if that fails, try to get it from the
        original.
        """
        return self.changes.get(key) or self._original[key]

    def __iter__(self):
        return iter(self.changes)

    def iteritems(self):
        return self.changes.iteritems()


class State(object):
    "Create a mutable state of a given cpu without mutating the CPU itself."
    def __init__(self, cpu, location=None):
        self.ram_iter, self.consumed = cpu.ram_iter(location)
        self.registers = DeltaDict(cpu.registers)
        self.ram = DeltaDict(dict(enumerate(cpu.ram)))
