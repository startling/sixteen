#!/usr/bin/env python


class HexRead(object):
    "A file-like object for reading hex dumps with possible whitespace."
    def __init__(self, path, mode="r"):
        self._fd = open(path, mode)

    def read(self, n):
        chars = []
        while n > 0:
            char = self._fd.read(1)
            if char in [" ", "\n", "\t"]:
                continue
            elif char == "":
                break
            else:
                chars.append(char)
                n -= .5
        return "".join(chars).decode("hex")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._fd.close()


def file_to_ram(f, cpu, bigendian=True, offset=0):
    """Given a file-like object if 16-bit words and a cpu object with a RAM
    attribute, read words from the file and store them in the RAM.
    """
    for n, _ in enumerate(cpu.RAM[offset:]):
        # read two bytes as ints
        word = [ord(c) for c in f.read(2)]
        # if there are exactly two bytes, go on
        if len(word) == 2:
            # unpack the top and the bottom of the word
            if bigendian:
                top, bottom = word
            else:
                bottom, top = word
            # bitshift the top up and then add to the bottom
            word_int = (top << 8) + bottom
            # set this n in the ram to that number
            cpu.RAM[n] = word_int
        # if there aren't two bytes, stop
        else:
            break

class OpcodeError(Exception):
    def __init__(self, value, address=None):
        self.value = value
        self.address = address

    def __str__(self):
        if self.address == None:
            return "'0x%x' is an unknown opcode." % self.value
        else:
            return ("0x%x at address 0x%04x is an unknown opcode." %
                    (self.value, self.address))
