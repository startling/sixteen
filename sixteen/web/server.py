import json
from twisted.internet import protocol, reactor
from txws import WebSocketFactory
from sixteen.dcpu16 import DCPU16
from sixteen.output import OutputCPU
from sixteen.memorymap import MemoryMap
from sixteen.characters import characters
from sixteen.words import bit_iter


class WebCPU(DCPU16, OutputCPU):
    # 16 char keyboard ring buffer at 0x9000 - 0x900f
    keyring = (0x9000, 0x900f)

    def __init__(self, protocol):
        "Given a twisted protocol, initialize a WebCPU."
        self.protocol = protocol
        # copy my own `registers` dict.
        self.registers = self._registers.copy()
        # initialize the keypointer offset
        self.key_offset = 0
        # this gets turned into True if we suspect the program is halting.
        self.halt = False
        self.RAM = MemoryMap(self.cells, [
            (self.vram, self.change_letter),
            (self.background, self.change_background),
            (self.chars, self.change_character),
        ])
        # read the default characters to the RAM
        self.RAM[self.chars[0]:] = characters

    def change_character(self, index, value):
        # return the whole character because half-characters are a pain.
        # if it's an even index, it's the first of a pair.
        if index % 2 == 0:
            top = value
            bottom = self.RAM[index + 1]
            location = (index - self.chars[0]) // 2
        else:
            top = self.RAM[index - 1]
            bottom = value
            location = ((index - 1) - self.chars[0]) // 2
        # use sixteen.output.OutputCPU.character to get a list of rows.
        rows = self.character(top, bottom)
        # and set the chars_changed to the rows
        self.protocol.chars_changed[location] = rows
        # ugly hack: make the frontend refresh the ones that have been changed
        # (might be too slow)
        for addr in (a for a in xrange(*self.vram) if (
            self.RAM[a] & 0b0000000001111111) == location):
             self.change_letter(addr, self.RAM[addr])

    def change_background(self, index, value):
        # format the background color as an html/css hex color.
        background = "#%02x%02x%02x" % self.color(value & 0x0f)
        self.protocol.change_background = background

    def change_letter(self, index, value):
        "This is called whenever a cell of vram is changed."
        # get the data from sixteen.output.OutputCPU.letter
        x, y, foreground, background, blink, char = self.letter(index, value)
        self.protocol.letters_changed.append({
            "x": x, "y": y, "char": char, "blink": blink,
            # format the background and foreground tuples as html/css colors.
            "foreground": "#%02x%02x%02x" % foreground,
            "background": "#%02x%02x%02x" % background,
        })

    def keyboard_input(self, key):
        """ Thanks, Rick.
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

    def is_halting(self):
        if self.halt:
            return True
        else:
            # if it's sub pc, 1, it's a halt...
            if self.RAM[self.registers["PC"]] == 0x85c3:
                self.halt = True
            else:
                # if it's something like :loop set pc, loop, it's a halt
                first = self.RAM[self.registers["PC"]]
                second = self.RAM[self.registers["PC"] + 1]
                if first == 0x7dc1 and second == self.registers["PC"]:
                    self.halt = True
            return self.halt


class DCPU16Protocol(protocol.Protocol):
    def __init__(self, code):
        # and the letters_changed list
        self.letters_changed = []
        self.chars_changed = {}
        self.change_background = None
        self.errors = []
        # intialize the cpu
        self.cpu = WebCPU(self)
        # read the code from the factory to the RAM
        self.cpu.RAM[:len(code)] = code

    def dataReceived(self, data):
        keypresses, count = json.loads(data)
        for k in keypresses:
            self.cpu.keyboard_input(ord(k))
        try:
            for _ in xrange(count):
                if not self.cpu.is_halting():
                    self.cpu.cycle()
                else:
                    break
        except Exception as e:
            self.errors.append(str(e))
        self.write_changes()

    def write_changes(self):
        "Write the changes to the websockets client and reset."
        changes = {
            "background": self.change_background,
            "cells": self.letters_changed,
            "characters": self.chars_changed,
            "errors": self.errors,
            "halt": self.cpu.halt,
        }
        self.transport.write(json.dumps(changes))
        self.letters_changed = []
        self.chars_changed = {}
        self.change_background = None
        self.errors = []
