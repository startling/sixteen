import json
from twisted.internet import protocol, reactor
from txws import WebSocketFactory
from sixteen.dcpu16 import DCPU16
from sixteen.memorymap import MemoryMap
from sixteen.characters import characters


class WebCPU(DCPU16):
    # vram is 0x8000 - 0x817f
    vram = (0x8000, 0x8180)
    height, width = (12, 32)

    # characters are 0x8180 - 0x827f
    chars = (0x8180, 0x8280)
    
    # background color is located at 0x8280
    background = (0x8280, 0x8281)

    def __init__(self, protocol):
        "Given a twisted protocol, initialize a WebCPU."
        self.protocol = protocol
        # copy my own `registers` dict.
        self.registers = self._registers.copy()
        self.RAM = MemoryMap(self.cells, [
            (self.vram, self.change_letter),
            (self.background, self.change_background),
        ])
        # read the default characters to the RAM
        self.RAM[self.chars[0]:] = characters

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
        background = (color & 0x00001111)
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

    def color(self, bits):
        "Turn a four-bit hrgb color into an HTML/CSS hex color."
        h = bits >> 3
        r = (bits & 0b0100) >> 2
        g = (bits & 0b0010) >> 1
        b = (bits & 0b0001)
        if h:
            r = r and 0xFF
            g = g and 0xFF
            b = b and 0xFF
        else:
            r = r and 0xAA
            b = b and 0xAA
            g = g and 0xAA
        return "#%02x%02x%02x" % (r, g, b)


class DCPU16Protocol(protocol.Protocol):
    def __init__(self, code):
        # intialize the cpu
        self.cpu = WebCPU(self)
        # and the letters_changed list
        self.letters_changed = []
        self.change_background = None
        # read the code from the factory to the RAM
        self.cpu.RAM[:len(code)] = code

    def dataReceived(self, data):
        #TODO: get keyboard input.
        self.cpu.cycle()
        self.write_changes()

    def write_changes(self):
        "Write the changes to the websockets client and reset."
        changes = {
            "background": self.change_background,
            "cells": self.letters_changed,
        }
        self.transport.write(json.dumps(changes))
        self.letters_changed = []
        self.change_background = None
