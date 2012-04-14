from PIL import Image
from sixteen.dcpu16 import DCPU16
from sixteen.output import OutputCPU
from sixteen.characters import characters


class ImageCPU(DCPU16, OutputCPU):
    char_width = 4
    char_height = 8

    def __init__(self):
        # copy my own `registers` dict.
        self.registers = self._registers.copy()
        # might do memory-mapping and delta-tracking soon-ish. for now, just a
        # list of integers.
        self.RAM = [0x0000] * 0x10000

    def dump(self, path):
        "Write an image of the current video ram to the given path."
        # initialize a new pil image.
        im = Image.new("RGB", (self.char_width * self.width, 
            self.char_height * self.height))
        for addr, val in ((a, self.RAM[a]) for a in xrange(*self.vram)):
            x, y, foreground, background, _, char = self.letter(addr, val)
            # find the location of the first word that describes this character.
            location = self.chars[0] + char
            rows = self.character(self.RAM[location], self.RAM[location + 1])
            # this is the true (pixel-wise) offsets for x and y
            offset_x = x * self.char_width
            offset_y = y * self.char_height
            for row_num, row in enumerate(rows):
                for col, pixel in enumerate(row):
                    coords = ((offset_x + col, offset_y + row_num))
                    # if the charmap here is 1, put the foreground
                    if pixel:
                        im.putpixel(coords, foreground)
                    # otherwise, put the background.
                    else:
                        im.putpixel(coords, background)
        im.save(path)
