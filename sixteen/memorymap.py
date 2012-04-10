# -*- coding: utf-8 -*-


class MemoryMap(object):
    def __init__(self, number, write=None, read=None, initial=0x0000):
        """Given a number of cells, two optional list of pairs of ranges to
        callbacks, and an optional initialization value, make a MemoryMap
        object. Here's how the write_callbacks work:

        "write_callbacks" should be a list like this: [
            ((0, 10), call)
        ], where "call" is a function that gets called whenever a value stored
        at 0-10 gets changed. The callback gets called with the changed value's
        index and the new value as its arguments.

        Read callbacks work similarly; they get called whenever a item is
        accessed, and must return a value.
        """
        if read == None:
            read = []
        if write == None:
            write = []
        self.read_callbacks = read
        self.write_callbacks = write
        self.number = number
        self._map = [initial] * number

    def __setitem__(self, n, value):
        # if this is a slice object
        if isinstance(n, slice):
            # call range with the slice's arguments and the values to set.
            for x, v in zip(range(*n.indices(len(self))), value):
                # set each thing in the range to the corresponding thing in the
                # values.
                self[x] = v
        else:
            # make sure that n is in bounds
            if n >= self.number or n < - self.number:
                raise IndexError("list index out of range")
            elif n < 0:
                n = self.number + n
            self._map[n] = value
            # check each callback
            for (start, end), callback in self.write_callbacks:
                # if it's within the bounds, call the callback
                if n >= start and n < end:
                    callback(n, value)

    def __getitem__(self, n):
        # if this is a slice object
        if isinstance(n, slice):
            # and then call range with the slice's arguments.
            return [self[x] for x in range(*n.indices(len(self)))]
        else:
            # make sure that n is in bounds
            if n >= self.number or n < - self.number:
                raise IndexError("list index out of range")
            elif n < 0:
                n = self.number + n
            # check each callback
            for (start, end), callback in self.read_callbacks:
                # if it's within the bounds, call the callback
                if n >= start and n < end:
                    return callback(n)
            else:
                # if it didn't get any of the callbacks, do nothing unusual.
                return self._map[n]

    def __len__(self):
        return self.number

    def register_write(self, (start, end), callback):
        "Register a new write callback."
        self.write_callbacks.append((start, end), callback)

    def register_read(self, (start, end), callback):
        "Register a new read callback."
        self.read_callbacks.append((start, end), callback)
