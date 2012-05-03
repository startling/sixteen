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

    def __init__(self):
        # initialize all the memory-mapping as nowhere
        self.mem_map_screen = None
        self.mem_map_font = None
        self.mem_map_palette = None
        # make a copy of the font
        self.font = characters[:]
        # and of the palette
        self.palette = palette[:]

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
                pass
            # if screen memory-mapping is on and the address is in that region
            if self.mem_map_screen is not None and (
                    0 <= addr - self.mem_map_screen < 0x182 ):
                pass
            # if palette memory-mapping is on and the address is in that region
            if self.mem_map_palette is not None and (
                    0 <= addr - self.mem_map_palette < len(self.palette)):
                pass
