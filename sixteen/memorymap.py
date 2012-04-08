# -*- coding: utf-8 -*-


class MemoryMap(object):
    def __init__(self, number, callbacks, initial=0x0000):
        """Given a number of cells, a list of pairs of ranges to callbacks, and
        an optional initialization value, make a MemoryMap object. Here's how
        the callbacks work:

        "callbacks" should be a list like this: [
            ((0, 10), call)
        ], where "call" is a function that gets called whenever a value stored
        at 0-10 gets changed. The callback gets called with the changed value's
        index and the new value as its arguments.
        """
        self.callbacks = callbacks
        self.number = number
        self._map = [initial] * number

    def __setitem__(self, n, value):
        # make sure that n is in bounds
        if n >= self.number or n < - self.number:
            raise IndexError("list index out of range")
        elif n < 0:
            n = self.number + n
        self._map[n] = value
        # check each callback
        for (start, end), callback in self.callbacks:
            # if it's within the bounds, call the callback
            if n >= start and n <= end:
                callback(n, value)

    def __getitem__(self, n):
        return self._map[n]

    def register(self, (start, end), callback):
        "Register a new callback."
        self.callbacks.append((start, end), callback)
