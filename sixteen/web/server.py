import json
from twisted.internet import protocol, reactor
from txws import WebSocketFactory
from sixteen.dcpu16 import DCPU16
from sixteen.memorymap import MemoryMap
from sixteen.characters import characters
from sixteen.words import bit_iter


class WebCPU(DCPU16):
    # vram is 0x8000 - 0x817f
    vram = (0x8000, 0x8180)
    height, width = (12, 32)

    # characters are 0x8180 - 0x827f
    chars = (0x8180, 0x8280)
    
    # background color is located at 0x8280
    background = (0x8280, 0x8281)

    # 16 char keyboard ring buffer at 0x9000 - 0x900f
    keyring = (0x9000, 0x900f)

    def __init__(self, protocol):
        "Given a twisted protocol, initialize a WebCPU."
        self.protocol = protocol
        # copy my own `registers` dict.
        self.registers = self._registers.copy()
        # initialize the keypointer offset
        self.key_offset = 0
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
        # oragnize the bits into columns
        columns = [
            [x for x in bit_iter(top >> 8, 8)][::-1],
            [x for x in bit_iter(top & 0xff, 8)][::-1],
            [x for x in bit_iter(bottom >> 8, 8)][::-1],
            [x for x in bit_iter(bottom & 0xff, 8)][::-1],
        ]
        # zip them, to rearrange them into rows.
        rows = zip(*columns)
        # and set the chars_changed to the rows
        self.protocol.chars_changed[location] = rows

    def change_background(self, index, value):
        background = self.color(value & 0x0f)
        self.protocol.change_background = background

    def change_letter(self, index, value):
        "This is called whenever a cell of vram is changed."
        offset = index - self.vram[0]
        # a display cell is ccccccccbiiiiiii
        # color is ffffbbbb.
        # bitshift away the character to get the color data
        color = value >> 8
        # bitshift away the lower four bits to get the foreground
        foreground = color >> 4
        # mask away the high four bits to get the background.
        background = color & 0b00001111
        # let the protocol know what changed.
        self.protocol.letters_changed.append({
            # calculate the x, y position.
            "x": offset % self.width,
            "y": offset // self.width,
            # this is the character number.
            "char": value & 0b0000000001111111,
            # and the blink bit.
            "blink": bool(value & 0b0000000010000000),
            # make hex colors from the foreground and background
            "foreground": self.color(foreground),
            "background": self.color(background),
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
        if self.RAM[self.key_offset] == 0:
            self.RAM[self.key_offset] = key
            self.key_offset = (self.key_offset + 1) % 16

    def color(self, bits):
        "Turn a four-bit hrgb color into an HTML/CSS hex color."
        h = bits >> 3
        r = (bits & 0b0100) >> 2
        g = (bits & 0b0010) >> 1
        b = (bits & 0b0001)
        r = r and 0xAA
        g = g and 0xAA
        b = b and 0xAA
        if h:
            r += 0x55 
            g += 0x55 
            b += 0x55 
        return "#%02x%02x%02x" % (r, g, b)


class DCPU16Protocol(protocol.Protocol):
    def __init__(self, code):
        # and the letters_changed list
        self.letters_changed = []
        self.chars_changed = {}
        self.change_background = None
        # intialize the cpu
        self.cpu = WebCPU(self)
        # read the code from the factory to the RAM
        self.cpu.RAM[:len(code)] = code

    def dataReceived(self, data):
        keypresses = json.loads(data)
        for k in keypresses:
            self.cpu.keyboard_input(ord(k))
        self.cpu.cycle()
        self.write_changes()

    def write_changes(self):
        "Write the changes to the websockets client and reset."
        changes = {
            "background": self.change_background,
            "cells": self.letters_changed,
            "characters": self.chars_changed,
        }
        self.transport.write(json.dumps(changes))
        self.letters_changed = []
        self.chars_changed = {}
        self.change_background = None
