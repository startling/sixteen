# -*- coding: utf-8 -*-

from sixteen.characters import characters
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
    font = characters

    def __init__(self):
        # initialize all the memory-mapping as nowhere
        self.mem_map_screen = None
        self.mem_map_font = None
        self.mem_map_palette = None
    
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
            #TODO: dump palette data
            pass
