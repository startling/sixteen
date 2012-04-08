# -*- coding: utf-8 -*-

import unittest
from sixteen.memorymap import MemoryMap


class TestMemoryMap(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryMap(20, [])

    def test_access(self):
        self.memory[5] = 20
        self.assertEquals(self.memory[5], 20)
        self.memory[5] = 23
        self.assertEquals(self.memory[5], 23)

    def test_out_of_bounds(self):
        self.assertRaises(IndexError, lambda: self.memory[25])
        self.assertRaises(IndexError, lambda: self.memory[-25])
        self.assertRaises(IndexError, lambda: self.memory[-25])

    def test_get_slices(self):
        self.memory[0] = 12
        self.memory[1] = 13
        self.assertEquals(self.memory[:2], [12, 13])

    def test_set_slices(self):
        self.memory[:2] = [12, 13]
        self.assertEquals(self.memory[0], 12)
        self.assertEquals(self.memory[1], 13)
