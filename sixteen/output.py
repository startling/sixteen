# -*- coding: utf-8 -*-

from sixteen.words import bit_iter


class OutputCPU(object):
    # background color is located at 0x8280
    background = (0x8280, 0x8281)

    # characters are 0x8180 - 0x827f
    chars = (0x8180, 0x8280)

    # vram is 0x8000 - 0x817f
    vram = (0x8000, 0x8180)
    height, width = (12, 32)

    def letter(self, index, value):
        # figure out the number of this from where the vram starts
        offset = index - self.vram[0]
        # a display cell is ccccccccbiiiiiii
        # color is ffffbbbb.
        # mask away the high bits to get the character code.
        char = value & 0b0000000001111111
        # mask and shift to get the blink bit.
        blink = bool((value & 0b0000000010000000) >> 7),
        # figure out the x and y position from the offset and width
        x = offset % self.width
        y = offset // self.width
        # bitshift away the character to get the color data
        color = value >> 8
        # bitshift away the lower four bits to get the foreground
        foreground = self.color(color >> 4)
        # mask away the high four bits to get the background.
        background = self.color(color & 0b00001111)
        return x, y, foreground, background, blink, char

    def character(self, top, bottom):
        "Turn two sixteen-bit words into a list representing a bitmap."
        # organize the bits into columns
        columns = [
            [x for x in bit_iter(top >> 8, 8)][::-1],
            [x for x in bit_iter(top & 0xff, 8)][::-1],
            [x for x in bit_iter(bottom >> 8, 8)][::-1],
            [x for x in bit_iter(bottom & 0xff, 8)][::-1],
        ]
        # zip them, to rearrange them into rows.
        return zip(*columns)

    def color(self, bits):
        "Turn a four-bit hrgb color into a three-tuple of r, g, b."
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
        return r, g, b
