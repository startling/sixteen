# -*- coding: utf-8 -*-


class RegisterMap(object):
    def __init__(self, registers, write=None, read=None):
        """Given a dictionary of registers and two optional list of pairs of
        ranges to callbacks, make a RegisterMap object. Here's how the
        write_callbacks work:

        "write_callbacks" should be a list like this: [ ("key", call) ], where
        "call" is a function that gets called whenever the value stores at
        "key" gets changed. The callback gets called with the changed value's
        index and the new value as its arguments.

        "read_callbacks" should be a similar list, but these callbacks get
        called whenever that key is *read*, and their returned value is
        returned.
        """
        if read == None:
            read = []
        if write == None:
            write = []
        self.read_callbacks = read
        self.write_callbacks = write
        self._map = registers
    
    def __setitem__(self, r, value):
        if not (r in self._map):
            raise KeyError(r)
        self._map[r] = value
        for r_other, callback in self.write_callbacks:
            if r == r_other:
                callback(r, value)

    def __getitem__(self, r):
        if not (r in self._map):
            raise KeyError(r)
        for r_other, callback in self.read_callbacks:
            if r == r_other:
                return callback(r)
        else:
            # if it didn't get any of the callbacks, do nothing unusual.
            return self._map[r]

    def __len__(self):
        return len(self._map)

    def items(self):
        return self._map.items()

    def register_write(self, r, callback):
        self.write_callbacks.append((r, callback))

    def register_read(self, r, callback):
        self.read_callbacks.append((r, callback))
