# -*- coding: utf-8 -*-


class Hardware(object):
    """Here's how hardware and interrupts work, if I've got it correctly.
    When starting, you do something like this (an example for the keyboard):
    
    SET A, n \ SET B, m \ HWI hardware_number

    Where `n` and `m` are device-specific hardware configuration values and
    `hard_ware` number is the ordinal number of the hardware device in the list
    of hardware of the CPU. this number is meant to be gotten with `HWN` (which
    sets A to the number of hardware devices) and `HWQ` (which gets information
    about the device at a specific ordinal number).
    """
    # the hardware id of the device
    identifier = 0x0000

    # version number of the device
    version = 0

    # manufacturer number of the device
    manufacturer = 0

    # the name of the hardware.
    name = ""

    def configure(self, registers):
        """Configure this device as per the configuration in the registers; this
        will probably be called when the program does a `HWI`.
        """
        pass

    #TODO: actually handle events?


class Keyboard(Hardware):
    """
    Name: Generic Keyboard (compatible)
    ID: 0x30cf7406
    Version: 1
    """
    name = "Generic Keyboard (compatible)"
    identifier = 0x30cf7406
    version = 1

    def __init__(self):
        self.mode = 0
        self.interrupt = False
        self.message = None
    
    def configure(self, registers):
        self.mode = registers["A"]
        if registers["A"] == 3:
            if registers["B"] == 0:
                self.interrupt = False
            else:
                self.interrupt = True
                self.message = registers["B"]
