# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16


class BaseDCPU16Test(object):
    def setUp(self):
        self.cpu = DCPU16()

    def run_instructions(self, words):
        self.cpu.ram[:len(words)] = list(words)
        count = 0
        while count < len(words):
            consumed = self.cpu.cycle()
            count += len(consumed)

    def assertRegister(self, name, value):
        self.assertEquals(self.cpu.registers[name], value)

    def assertRAM(self, addr, value):
        self.assertEquals(self.cpu.ram[addr], value)


class TestSet(BaseDCPU16Test, unittest.TestCase):
    def test_set_ram_pointer(self):
        self.run_instructions([
            # set ram addres 0x1337 to 0xbeef
            0x7be1, 0x1337, 0xbeef
        ])
        self.assertRAM(0x1337, 0xbeef)

    def test_set_register(self):
        self.run_instructions([
            # set a, 0xbeef
            0x03e1, 0xbeef,
            # set x, 0x1337
            0x0fe1, 0x1337,
        ])
        self.assertRegister("A", 0xbeef)
        self.assertRegister("X", 0x1337)


class TestAdd(BaseDCPU16Test, unittest.TestCase):
    def test_add_pointer_literal(self):
        self.run_instructions([
            # set ram addres 0x1337 to 0xbeef
            0x7be1, 0x1337, 0xbeef,
            # add 0x1000 to 0xbeef
            0x7be2, 0x1337, 0x1000
        ])
        self.assertRAM(0x1337, 0xbeef + 0x1000)
        self.assertRegister("EX", 0x0)

    def test_add_overflow(self):
        self.run_instructions([
            # set ram addres 0x1337 to 0xffff
            0x7be1, 0x1337, 0xffff,
            # add 0x1000 to 0xffff
            0x7be2, 0x1337, 0x1000
        ])
        self.assertRAM(0x1337, 0x0fff)
        self.assertRegister("EX", 0x1)


class TestSub(BaseDCPU16Test, unittest.TestCase):
    def test_sub_pointer_literal(self):
        self.run_instructions([
            # set ram addres 0x1337 to 0xbeef
            0x7be1, 0x1337, 0xbeef,
            # sub 0x1000 from 0xbeef
            0x7be3, 0x1337, 0x1000
        ])
        self.assertRAM(0x1337, 0xbeef - 0x1000)
        self.assertRegister("EX", 0x0)

    def test_sub_underflow(self):
        self.run_instructions([
            # sub 1 from 0
            0x7be3, 0x1337, 0x0001
        ])
        self.assertRAM(0x1337, 0xffff)
        self.assertRegister("EX", 0xffff)


class TestMul(BaseDCPU16Test, unittest.TestCase):
    def test_mul_pointer_literal(self):
        self.run_instructions([
            # set ram addres 0x1337 to 80
            0x7be1, 0x1337, 80,
            # mul 80 by 2
            0x7be4, 0x1337, 2,
        ])
        self.assertRAM(0x1337, 160)
        self.assertRegister("EX", 0x0)

    def test_mul_pointer_literal(self):
        self.run_instructions([
            # set ram addres 0x1337 to 0xf000
            0x7be1, 0x1337, 0xf000,
            # mul 0xf000 by 2
            0x7be4, 0x1337, 2,
        ])
        self.assertRAM(0x1337, 0xe000)
        # calculate the overflow as per the spec: ((b*a)>>16)&0xffff
        self.assertRegister("EX", ((0xf000 * 2) >> 16) & 0xffff)


class TestDiv(BaseDCPU16Test, unittest.TestCase):
    def test_div_pointer_literal(self):
        self.run_instructions([
            # set ram addres 0x1337 to 80
            0x7be1, 0x1337, 80,
            # divide 80 by 2
            0x7be6, 0x1337, 2,
        ])
        self.assertRAM(0x1337, 40)
        self.assertRegister("EX", 0x0)

    def test_div_underflow(self):
        self.run_instructions([
            # set ram addres 0x1337 to 1
            0x7be1, 0x1337, 0x1,
            # divide 0xf000 by 100
            0x7be6, 0x1337, 100,
        ])
        self.assertRAM(0x1337, 0)
        # calculate the overflow as per the spec: ((b<<16)/a)&0xffff)
        self.assertRegister("EX", ((1 << 16) // 100) & 0xffff)


class TestAnd(BaseDCPU16Test, unittest.TestCase):
    def test_and_pointer_literal(self):
        self.run_instructions([
            # set ram addres 0xbeef to 1
            0x7be1, 0xbeef, 1,
            # AND it by 1
            0x7be9, 0xbeef, 1,
        ])
        self.assertRAM(0xbeef, 1)


class TestMod(BaseDCPU16Test, unittest.TestCase):
    def test_mod(self):
        self.run_instructions([
            # set ram addres 0xbeef to 7
            0x7be1, 0xbeef, 7,
            # % 2
            0x7be8, 0xbeef, 2,
        ])
        self.assertRAM(0xbeef, 1)


class TestBor(BaseDCPU16Test, unittest.TestCase):
    def test_bor(self):
        self.run_instructions([
            # set ram addres 0xbeef to 0
            0x7be1, 0xbeef, 0,
            # | 1
            0x7bea, 0xbeef, 1,
        ])
        self.assertRAM(0xbeef, 1)


class TestXor(BaseDCPU16Test, unittest.TestCase):
    def test_xor(self):
        self.run_instructions([
            # set ram addres 0xbeef to 1
            0x7be1, 0xbeef, 1,
            # ^ 2
            0x7beb, 0xbeef, 1,
        ])
        self.assertRAM(0xbeef, 0)
