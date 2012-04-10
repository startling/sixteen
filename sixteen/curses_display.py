# -*- coding: utf-8 -*-

import curses 
import locale
from sixteen.dcpu16 import DCPU16
from sixteen.memorymap import MemoryMap


class Curses(object):
    "A basic context manager for the main curses screen."
    def __init__(self):
        "Initialize a main curses screen."
        locale.setlocale(locale.LC_ALL, '')
        self.coding = locale.getpreferredencoding()
        self.screen = curses.initscr()

    def __enter__(self):
        "A bunch of crap we need to call to make curses do anything."
        # initialize color
        curses.start_color()
        # don't echo keypresses
        curses.noecho()
        # give us keypresses before the user presses enter
        curses.cbreak()
        # give us special keys as multibyte escape sequences
        self.screen.keypad(0)
        # and then return this object
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        "Close all of the curses crap."
        # require enter again
        curses.nocbreak()
        # turn of multibyte escapes
        self.screen.keypad(0)
        # and turn echo back on
        curses.echo()
        # end windows. to be honest I dunno what this does, but the curses
        # manual says to do it
        curses.endwin()

    def __getattr__(self, name):
        "If this object doesn't have a thing, check the screen too."
        return getattr(self.screen, name)


class TerminalCPU(DCPU16):
    # speculative: vram starts at 0x8000 and ends at 0x8180
    vram = (0x8000, 0x8180)
    # speculative: height, width of the display
    height, width = (12, 32)

    def __init__(self, c):
        """Given a curses window, initialize a cpu with memory-mapped output to
        that window.
        """
        self.window = c
        self.RAM = MemoryMap(self.cells, [(self.vram, self.curses_write)])
        # copy my own `registers` dict.
        self.registers = self._registers.copy()

    def curses_write(self, position, value):
        "This gets called whenever a cell within the vram is changed."
        # low seven bits is the character in ascii, so mask away all the rest
        # the rest is unspec'd color data probably.
        char = chr(value & 0b0000000001111111)
        # subtract the lower bound of the vram the given position
        offset = position - self.vram[0]
        # calculate the x, y position.
        x = offset % self.width
        y = offset // self.width
        # and then add the character
        self.window.addch(y, x, char)
