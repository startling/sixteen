# -*- coding: utf-8 -*-

from sixteen.display_constants import characters, palette
from sixteen.devices import Hardware


class LEM1802(Hardware):
    """
    Name: LEM1802 - Low Energy Monitor
    ID: 0x7349f615, version: 0x1802
    Manufacturer: 0x1c6c8b36 (NYA_ELEKTRISKA)
    """
    name = "LEM1802 - Low Energy Monitor"
    identifier = 0x7349f615
    version = 0x1802
    manufacturer = 0x1c6c8b36

    def __init__(self, change_font, change_screen, change_palette):
        # initialize all the memory-mapping as nowhere
        self.mem_map_screen = None
        self.mem_map_font = None
        self.mem_map_palette = None
        # make a copy of the font
        self.font = characters[:]
        # and of the palette
        self.palette = palette[:]
        # save the callbacks
        self.change_font = change_font
        self.change_screen = change_screen
        self.change_palette = change_palette

    def on_interrupt(self, registers, ram):
        "See docs/lem1802 for more details regarding these."
        if registers["A"] == 0:
            # set the vram location to B
            self.mem_map_screen = registers["B"]
        elif registers["A"] == 1:
            # set the fontram location to B
            self.mem_map_font = registers["B"]
        elif registers["A"] == 2:
            # set the palette location to B
            self.mem_map_palette = registers["B"]
        elif registers["A"] == 3:
            #TODO: set border color
            pass
        elif registers["A"] == 4:
            # dump font data
            start = registers["B"]
            end = start + len(self.font)
            ram[start:end] = self.font
        elif registers["A"] == 5:
            # dump palette data
            start = registers["B"]
            end = start + len(self.palette)
            ram[start:end] = self.palette

    def on_cycle(self, changed_registers, changed_ram):
        for addr, value in changed_ram.iteritems():
            # if font memory-mapping is on and the address is in that region
            if self.mem_map_font is not None and (
                    0 <= addr - self.mem_map_font < len(self.font)):
                self.font[addr - self.mem_map_font] = value
                self.change_font(addr, value)
            # if screen memory-mapping is on and the address is in that region
            if self.mem_map_screen is not None and (
                    0 <= addr - self.mem_map_screen < 0x182 ):
                # The LEM1802 has no internal video ram, but rather relies on being assigned
                # an area of the DCPU-16 ram. The size of this area is 386 words, and is
                # made up of 32x12 cells of the following bit format (in LSB-0):
                #     ffffbbbbBccccccc
                # The lowest 7 bits (ccccccc) select define character to display.
                # ffff and bbbb select which foreground and background color to use.
                # If B (bit 7) is set the character color will blink slowly.
                foreground = (0b1111000000000000 & value) >> 12
                background = (0b0000111100000000 & value) >> 8
                blink = (0b0000000010000000 & value) >> 7
                char = 0b1111111110000000 & value
                index = addr - self.mem_map_screen
                self.change_screen(index, foreground, background, blink, char)
            # if palette memory-mapping is on and the address is in that region
            if self.mem_map_palette is not None and (
                    0 <= addr - self.mem_map_palette < len(self.palette)):
                self.palette[addr - self.mem_map_palette] = value
                self.change_palette(addr, value)
