import json
from twisted.internet import protocol, reactor
from txws import WebSocketFactory
from sixteen.dcpu16 import DCPU16
from sixteen.devices import Keyboard
from sixteen.screen import LEM1802


class DCPU16Protocol(protocol.Protocol):
    cycle_counter = 0

    def __init__(self, code):
        # and the letters_changed list
        self.letters_changed = {}
        self.chars_changed = {}
        self.border_color = None
        self.errors = []
        self.keyboard = Keyboard()
        self.display = LEM1802(self.change_font, self.change_letter,
                self.change_palette)
        # intialize the cpu
        self.cpu = DCPU16([self.keyboard, self.display])
        # read the code from the factory to the RAM
        self.cpu.ram[:len(code)] = code

    def change_palette(self, index, value):
        #TODO: change the palette -- not sure how this will work.
        pass

    def change_font(self, index, value):
        #TODO: change a font character.
        pass

    def change_border(self, index, value):
        #TODO: format the border color as an html/css hex color.
        pass

    def change_letter(self, index, foreground, background, blink, char):
        "This is called whenever a cell of vram is changed."
        x, y = divmod(index, 32)
        self.letters_changed[(x, y)] = {
            "x": x, "y": y, "char": char, "blink": blink,
            # format the background and foreground tuples as html/css colors.
            "foreground": "#%02x%02x%02x" % foreground,
            "background": "#%02x%02x%02x" % background,
        }

    def dataReceived(self, data):
        # get the keypresses and the number of cycles from the frontend
        keypresses, count = json.loads(data)
        for k in keypresses:
            # hand these to the keyboard
            self.keyboard.register_keypress(k)
        try:
            # cycle as many times as we're supposed to,
            for _ in xrange(count):
                self.cpu.cycle()
        # if we get any errors, let the frontend know.
        except Exception as e:
            self.errors.append(str(e))
        # and then pass everything to the frontend.
        self.write_changes()

    def write_changes(self):
        "Write the changes to the websockets client and reset."
        changes = {
            # None if there's no new background color, otherwise a color.
            "background": self.border_color,
            # the cells that have been changed since last time
            "cells": self.letters_changed.values(),
            # the characters (fonts) that have been changed
            "characters": self.chars_changed,
            # any errors we've encountered
            "errors": self.errors,
            # whether the frontend should stop.
            "halt": False,
        }
        # reset everything
        self.transport.write(json.dumps(changes))
        self.letters_changed = {}
        self.chars_changed = {}
        self.border_color = None
        self.errors = []
