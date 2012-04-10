# -*- coding: utf-8 -*-


class RegisterMap(object):
    def __init__(self, registers, write=None, read=None, initial=0x0000):
        """TODO: Documentation. Is very similar to MemoryMap.

        registers is a dictionary of register --> int
        """

        if read == None:
            read = []
        if write == None:
            write = []
        self.read_callbacks = read
        self.write_callbacks = write
        self.registers = registers
        self._map = registers
    
    def __setitem__(self, r, value):
        # FIXME: I have no idea what this does -- reynir
        # if this is a slice object
        if isinstance(r, slice):
            pass
        else:
            if not (r in self._map):
                raise KeyError(r)
            self._map[r] = value
            for r_other, callback in self.write_callbacks:
                if r == r_other:
                    callback(r, value)

    def __getitem__(self, r):
        # FIXME: Again, no idea -- reynir
        # if this is a slice object
        if isinstance(r, slice):
            pass
        else:
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
