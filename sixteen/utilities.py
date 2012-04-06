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
