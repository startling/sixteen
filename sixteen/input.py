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
        location = self.keyring[0] + self.key_offset
        if self.RAM[location] == 0:
            self.RAM[location] = key
            self.key_offset = (self.key_offset + 1) % 16
