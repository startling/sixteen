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
