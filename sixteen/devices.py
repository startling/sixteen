# -*- coding: utf-8 -*-

from collections import deque


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

    def on_interrupt(self, registers, ram):
        """This gets called when a program does HWI, usually. It gets
        dictionaries of the current state's registers and RAM, which it can
        modify as it pleases. Whatever gets returned gets ignored.
        """
        pass

    def on_cycle(self, changed_registers, changed_ram):
        """This gets called for each device for each cycle. If it returns a
        thing (an integer no greater than 0xffff, ideally), that thing gets
        used as the message for an intterupt. That should be its only means of
        communicating to the CPU; it shouldn't modify the changed_ram or
        changed_registers.
        """
        pass


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
        self.interrupt_mode = False
        self.message = None
        # append when we get new keypresses, popleft to take them out
        self.queue = deque()
    
    def on_interrupt(self, registers, ram):
        """From the docs for the generic keyboard:
        0 - Clear keyboard buffer
        1 - Store next key typed in C register, or 0 if the buffer is empty
        2 - Set C register to 1 if the key specified by the B register is pressed, or
            0 if it's not pressed
        3 - If register B is non-zero, turn on interrupts with message B. If B
            is zero, disable interrupts
        """
        if registers["A"] == 0:
            self.queue.clear()
        elif registers["A"] == 1:
            #NOTE: this behavior might be wrong; the spec says to store the
            # _next_ key, which is ambiguous.
            if len(self.queue):
                registers["C"] = self.queue.popleft()
            else:
                registers["C"] = 0
        elif registers["A"] == 2:
            value = self.queue.popleft()
            registers["C"] = int(value == registers["B"])
        elif registers["A"] == 3:
            if registers["B"] == 0:
                self.interrupt_mode = False
            else:
                self.interrupt_mode = True
                self.message = registers["B"]

    def register_keypress(self, keypress):
        """Call this when you get a keypress from whatever source and want to add
        it to the keyboard's buffer.
        
        This should be a number like the following (from the docs):
        > Key numbers are:
        > 0x10: Backspace
        > 0x11: Return
        > 0x12: Insert
        > 0x13: Delete
        > 0x20-0x7f: ASCII characters
        > 0x80: Arrow up
        > 0x81: Arrow down
        > 0x82: Arrow left
        > 0x83: Arrow right
        > 0x90: Shift
        > 0x91: Control
        """
        self.queue.append(keypress)
        
    def on_cycle(self, changed_registers, changed_ram):
        if self.interrupt_mode and len(self.queue):
            return self.message
