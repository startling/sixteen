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
        self.consumed = []
        self.cells = cpu.cells
        self.ram_iter = self.ram_iterator(location)
        self.registers = DeltaDict(cpu.registers)
        self.ram = DeltaDict(dict(enumerate(cpu.ram)))

    def pop(self):
        "Pop from the cpu's stack."
        value = self.ram[self.registers["SP"]]
        self.registers["SP"] += 1
        self.registers["SP"] %= 0x10000
        return value

    def push(self, value):
        "Push to the cpu's stack."
        self.registers["SP"] -= 1
        self.registers["SP"] %= 0x10000
        self.ram[self.registers["SP"]] = value

    def ram_iterator(self, location):
        """Return an iterator over this cpu's RAM and a list that will be updated
        whenever a value is drawn.
        """
        place = location or self.registers["PC"]
        while True:
            self.consumed.append(self.ram[place])
            yield self.ram[place]
            # increment the place counter, handling overflow if applicable.
            place += 1
            place %= self.cells
