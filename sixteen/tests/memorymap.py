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

    def test_negative_access(self):
        self.memory[-5] = 30
        self.assertEquals(self.memory[15], 30)

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


class TestCallbacks(unittest.TestCase):
    def setUp(self):
        self.my_dict = {}
        def listappend(n, v):
            self.my_dict[n] = v
        self.memory = MemoryMap(20, write=[((0, 16), listappend)])

    def test_set(self):
        self.memory[5] = 20
        self.assertEquals(self.my_dict, {5: 20})

    def test_set_negative(self):
        self.memory[-5] = 20
        self.assertEquals(self.my_dict, {15: 20})

    def test_not_called(self):
        self.memory[19] = 31
        self.memory[-1] = 29
        self.assertNotIn(19, self.my_dict.keys())
        self.assertNotIn(-1, self.my_dict.keys())


class TestWriteCallbacks(unittest.TestCase):
    def setUp(self):
        def times_two(n):
            return n * 2
        self.memory = MemoryMap(20, read=[((0, 16), times_two)])

    def test_get(self):
        self.assertEquals(self.memory[1], 2)
        self.assertEquals(self.memory[6], 12)

    def test_set(self):
        self.memory[2] = 5
        self.assertEquals(self.memory[2], 4)

    def test_negative(self):
        self.assertEquals(self.memory[-19], 2)
        self.memory[19] = 5
        self.assertEquals(self.memory[-1], 5)

    def test_not_called(self):
        self.memory[19] = 5
        self.assertEquals(self.memory[19], 5)
