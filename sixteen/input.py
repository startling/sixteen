# -*- coding: utf-8 -*-


class InputCPU(object):
    # 16 char keyboard ring buffer at 0x9000 - 0x900f
    keyring = (0x9000, 0x900f)

    def keyboard_input(self, key):
        """ Given the ascii code for the key pressed, put it into memory.

        > < startling> so how does input work? writes to the first location
        >     between 0x9000 - 0x900f that's not zero?
        > < Rick> virtualkeyboard has an internal offset that starts at 0
        > < Rick> it checks if [0x9000+offset] is zero
        > < Rick> if it's not
        > < Rick> it drops input
        > < Rick> if it is, it sets the value to the key and (offset+1)%16
        > < startling> wonderful.
        """
        pointer = self.RAM[0x9010]
        if not 0x9000 <= pointer < 0x9010:
            pointer = 0x9000
        n = pointer + 1
        if n >= 0x9010:
            n = 0x9000
        if self.RAM[n] == 0:
            self.RAM[n] = key
            pointer = n
        self.RAM[0x9010] = pointer
