# -*- coding: utf-8 -*-

import unittest
from sixteen.dcpu16 import DCPU16
from sixteen.bits import as_signed, from_signed


class BaseDCPU16Test(object):
    def setUp(self):
        self.cpu = DCPU16()

    def run_instructions(self, words):
        self.cpu.ram[:len(words)] = list(words)
        while self.cpu.registers["PC"] < len(words):
            self.cpu.cycle()

    def assertRegister(self, name, value):
        self.assertEquals(self.cpu.registers[name], value)

    def assertRAM(self, addr, value):
        self.assertEquals(self.cpu.ram[addr], value)


class TestSet(BaseDCPU16Test, unittest.TestCase):
    def test_set_ram_pointer(self):
        self.run_instructions([
            # set ram address 0x1337 to 0xbeef
            0x7fc1, 0x1337, 0xbeef
        ])
        self.assertRAM(0x1337, 0xbeef)

    def test_set_register(self):
        self.run_instructions([
            # set a, 0xbeef
            0x7c01, 0xbeef,
            # set x, 0x1337
            0x7c61, 0x1337,
        ])
        self.assertRegister("A", 0xbeef)
        self.assertRegister("X", 0x1337)

    def test_set_from_register(self):
        self.run_instructions([
            # set a, 0xbeef
            0x7c01, 0xbeef,
            # set x, a
            0x0061
        ])
        self.assertRegister("A", 0xbeef)
        self.assertRegister("X", 0xbeef)

    def test_set_to_register_pointer(self):
        self.run_instructions([
            # set a, 0xbeef
            0x7c01, 0xbeef,
            # set [a], 0xdead
            0x7d01, 0xdead
        ])
        self.assertRAM(0xbeef, 0xdead)

    def test_set_from_register_pointer(self):
        self.run_instructions([
            # set a, 0xbeef
            0x7c01, 0xbeef,
            # set ram address 0xbeef to 0x6666
            0x7fc1, 0xbeef, 0x6666,
            # set 0xdead, [a]
            0x23c1, 0xdead
        ])
        self.assertRAM(0xdead, 0x6666)

    def test_set_to_register_plus_next_word(self):
        self.run_instructions([
            # set a, 0xdead
            0x7c01, 0xdead,
            # set ram address 0xdeae to 0x6666
            0x7fc1, 0xdeae, 0x6666,
            # set b, [a + 1]
            0x4021, 1,
            # set [a + 1], 0x1337
            0x7e01, 0x0001, 0x1337
        ])
        self.assertRAM(0xdeae, 0x1337)

    def test_set_from_register_plus_next_word(self):
        self.run_instructions([
            # set a, 0xdead
            0x7c01, 0xdead,
            # set ram address 0xdeae to 0x6666
            0x7fc1, 0xdeae, 0x6666,
            # set b, [a + 1]
            0x4021, 1
        ])
        self.assertRegister("B", 0x6666)

    def test_get_pc(self):
        self.run_instructions([
            # set a, a (no-op)
            0x0001,
            # set a, PC  
            0x7001,
        ])
        self.assertRegister("A", 1)

    def test_get_sp(self):
        self.run_instructions([
            # set a, SP
            0x6c01,
        ])
        self.assertRegister("A", 0)

    def test_get_ex(self):
        self.run_instructions([
            # add two literals together, for EX
            0x7fe2, 0xffff, 0xffff,
            # set a, EX
            0x7401
        ])
        self.assertRegister("A", 1)

    def test_set_from_literal(self):
        self.run_instructions([
            # set a, -1 (short literal: 0x20)
            0x8001,
            # set b, 1 (short literal: 0x22)
            0x8821
        ])
        self.assertRegister("A", 0xffff)
        self.assertRegister("B", 1)


class TestAdd(BaseDCPU16Test, unittest.TestCase):
    def test_add_pointer_literal(self):
        self.run_instructions([
            # set ram address 0x1337 to 0xbeef
            0x7fc1, 0x1337, 0xbeef,
            # add 0x1000 to 0xbeef
            0x7fc2, 0x1337, 0x1000
        ])
        self.assertRAM(0x1337, 0xbeef + 0x1000)
        self.assertRegister("EX", 0x0)

    def test_add_overflow(self):
        self.run_instructions([
            # set ram address 0x1337 to 0xffff
            0x7fc1, 0x1337, 0xffff,
            # add 0x1000 to 0xffff
            0x7fc2, 0x1337, 0x1000
        ])
        self.assertRAM(0x1337, 0x0fff)
        self.assertRegister("EX", 0x1)


class TestSub(BaseDCPU16Test, unittest.TestCase):
    def test_sub_pointer_literal(self):
        self.run_instructions([
            # set ram address 0x1337 to 0xbeef
            0x7fc1, 0x1337, 0xbeef,
            # sub 0x1000 from 0xbeef
            0x7fc3, 0x1337, 0x1000
        ])
        self.assertRAM(0x1337, 0xbeef - 0x1000)
        self.assertRegister("EX", 0x0)

    def test_sub_underflow(self):
        self.run_instructions([
            # sub 1 from 0
            0x7fc3, 0x1337, 0x0001
        ])
        self.assertRAM(0x1337, 0xffff)
        self.assertRegister("EX", 0xffff)


class TestMul(BaseDCPU16Test, unittest.TestCase):
    def test_mul_pointer_literal(self):
        self.run_instructions([
            # set ram address 0x1337 to 80
            0x7fc1, 0x1337, 80,
            # mul 80 by 2
            0x7fc4, 0x1337, 2,
        ])
        self.assertRAM(0x1337, 160)
        self.assertRegister("EX", 0x0)

    def test_mul_pointer_literal(self):
        self.run_instructions([
            # set ram address 0x1337 to 0xf000
            0x7fc1, 0x1337, 0xf000,
            # mul 0xf000 by 2
            0x7fc4, 0x1337, 2,
        ])
        self.assertRAM(0x1337, 0xe000)
        # calculate the overflow as per the spec: ((b*a)>>16)&0xffff
        self.assertRegister("EX", ((0xf000 * 2) >> 16) & 0xffff)


class TestMli(BaseDCPU16Test, unittest.TestCase):
    def test_mli(self):
        self.run_instructions([
            # set ram address 0x1337 to 80
            0x7fc1, 0x1337, 80,
            # mul 80 by 2
            0x7fc5, 0x1337, from_signed(-2),
        ])
        self.assertRAM(0x1337, from_signed(-160))

    def test_mli_both_negative(self):
        self.run_instructions([
            # set ram address 0x1337 to 80
            0x7fc1, 0x1337, from_signed(-10),
            # mul 80 by 2
            0x7fc5, 0x1337, from_signed(-10),
        ])
        self.assertRAM(0x1337, 100)
        self.assertRegister("EX", 0x0)


class TestDiv(BaseDCPU16Test, unittest.TestCase):
    def test_div_pointer_literal(self):
        self.run_instructions([
            # set ram address 0x1337 to 80
            0x7fc1, 0x1337, 80,
            # divide 80 by 2
            0x7fc6, 0x1337, 2,
        ])
        self.assertRAM(0x1337, 40)
        self.assertRegister("EX", 0x0)

    def test_div_underflow(self):
        self.run_instructions([
            # set ram address 0x1337 to 1
            0x7fc1, 0x1337, 0x1,
            # divide 0xf000 by 100
            0x7fc6, 0x1337, 100,
        ])
        self.assertRAM(0x1337, 0)
        # calculate the overflow as per the spec: ((b<<16)/a)&0xffff)
        self.assertRegister("EX", ((1 << 16) // 100) & 0xffff)


class TestAnd(BaseDCPU16Test, unittest.TestCase):
    def test_and_pointer_literal(self):
        self.run_instructions([
            # set ram address 0xbeef to 1
            0x7fc1, 0xbeef, 1,
            # AND it by 1
            0x7fca, 0xbeef, 1,
        ])
        self.assertRAM(0xbeef, 1)


class TestMod(BaseDCPU16Test, unittest.TestCase):
    def test_mod(self):
        self.run_instructions([
            # set ram address 0xbeef to 7
            0x7fc1, 0xbeef, 7,
            # % 2
            0x7fc8, 0xbeef, 2,
        ])
        self.assertRAM(0xbeef, 1)


class TestBor(BaseDCPU16Test, unittest.TestCase):
    def test_bor(self):
        self.run_instructions([
            # set ram address 0xbeef to 0
            0x7fc1, 0xbeef, 0,
            # | 1
            0x7fcb, 0xbeef, 1,
        ])
        self.assertRAM(0xbeef, 1)


class TestXor(BaseDCPU16Test, unittest.TestCase):
    def test_xor(self):
        self.run_instructions([
            # set ram address 0xbeef to 1
            0x7fc1, 0xbeef, 1,
            # ^ 2
            0x7fcc, 0xbeef, 1,
        ])
        self.assertRAM(0xbeef, 0)


class TestShr(BaseDCPU16Test, unittest.TestCase):
    def test_shr(self):
        self.run_instructions([
            # set ram address 0xbeef to 1
            0x7fc1, 0xbeef, 0b100,
            # >> 2
            0x7fcd, 0xbeef, 2,
        ])
        self.assertRAM(0xbeef, 0b1)

    def test_shr_underflow(self):
        self.run_instructions([
            # set ram address 0xbeef to 1
            0x7fc1, 0xbeef, 0b100,
            # >> 2
            0x7fcd, 0xbeef, 3,
        ])
        self.assertRAM(0xbeef, 0)
        # overflow is: ((b<<16)>>a)&0xffff)
        self.assertRegister("EX", ((0b100 << 16) >> 3) & 0xffff)


class TestShl(BaseDCPU16Test, unittest.TestCase):
    def test_shl(self):
        self.run_instructions([
            # set ram address 0xbeef to 1
            0x7fc1, 0xbeef, 0b1,
            # << 2
            0x7fcf, 0xbeef, 2,
        ])
        self.assertRAM(0xbeef, 0b100)

    def test_shl_overflow(self):
        self.run_instructions([
            # set ram address 0xbeef to 1
            0x7fc1, 0xbeef, 0b1000000000000000,
            # << 1
            0x7fcf, 0xbeef, 1,
        ])
        self.assertRAM(0xbeef, 0)
        # overflow is: ((b<<a)>>16)&0xffff)
        self.assertRegister("EX", ((0b1000000000000000 << 1) >> 16) & 0xffff)


class TestConditionals(BaseDCPU16Test, unittest.TestCase):
    def test_ifb(self):
        self.run_instructions([
            # if (0b1 & 0b1) != 0 (True)
            0x7ff0, 0b1, 0b1,
            # set a to 0xbeef (this should get evaluated)
            0x7c01, 0xbeef,
            # if (0b0 & 0b0) != 0 (False)
            0x7ff0, 0b0, 0b0,
            # set b to 0xdead (this *shouldn't* get evaluated)
            0x7c21, 0xdead
        ])
        self.assertRegister("A", 0xbeef)
        self.assertRegister("B", 0x0)

    def test_ifc(self):
        self.run_instructions([
            # if (0b1 & 0b1) == 0 (False)
            0x7ff1, 0b1, 0b1,
            # set a to 0xdead (this shouldn't get evaluated)
            0x7c01, 0xdead,
            # if (0b0 & 0b0) == 0 (True)
            0x7ff1, 0b0, 0b0,
            # set b to 0xbeef (this *should* get evaluated)
            0x7c21, 0xbeef
        ])
        self.assertRegister("A", 0x0)
        self.assertRegister("B", 0xbeef)

    def test_ife(self):
        self.run_instructions([
            # if 0xcafe == 0xcafe (True)
            0x7ff2, 0xcafe, 0xcafe,
            # set a to 0xbeef (this should get evaluated)
            0x7c01, 0xbeef,
            # if 0x1337 == 0xdead (False)
            0x7ff2, 0xdead, 0x1337,
            # set b to 0xdead (this shouldn't get evaluated)
            0x7c21, 0xdead
        ])
        self.assertRegister("A", 0xbeef)
        self.assertRegister("B", 0x0)

    def test_ifn(self):
        self.run_instructions([
            # if 0x1337 != 0xdead (True)
            0x7ff3, 0x1337, 0xdead,
            # set a to 0xbeef (this should get evaluated)
            0x7c01, 0xbeef,
            # if 0xcafe != 0xcafe (False)
            0x7ff3, 0xcafe, 0xcafe,
            # set b to 0xdead (this shouldn't get evaluated)
            0x7c21, 0xdead
        ])
        self.assertRegister("A", 0xbeef)
        self.assertRegister("B", 0x0)


    def test_ifg(self):
        self.run_instructions([
            # if 0xcafe > 0x1000 (True)
            # notice that these words are backwards, because a gets evaluated
            # first yet is the second operand.
            0x7ff4, 0x1000, 0xcafe,
            # set a to 0xbeef (this should get evaluated)
            0x7c01, 0xbeef,
            # if 0x1337 > 0x7331 (False)
            0x7ff4, 0x7331, 0x1337,
            # set b to 0xdead (this shouldn't get evaluated)
            0x7c21, 0xdead
        ])
        self.assertRegister("A", 0xbeef)
        self.assertRegister("B", 0x0)

    def test_ifl(self):
        self.run_instructions([
            # if 0xcafe < 0x1000 (False)
            # these are backwards too.
            0x7ff6, 0x1000, 0xcafe,
            # set a to 0xdead (this shouldn't get evaluated)
            0x7c01, 0xdead,
            # if 0x1337 > 0x7331 (False)
            0x7ff6, 0x7331, 0x1337,
            # set b to 0xbeef (this should get evaluated)
            0x7c21, 0xbeef
        ])
        self.assertRegister("A", 0x0)
        self.assertRegister("B", 0xbeef)


class TestAdx(BaseDCPU16Test, unittest.TestCase):
    def test_adx(self):
        self.run_instructions([
            # set a, 20
            0x7c01, 20,
            # set b, 10
            0x7c21, 10,
            # add 0xffff, 0xffff (for EX):
            0x7fe2, 0xffff, 0xffff,
            # adx a, b
            0x041a
        ])
        self.assertRegister("A", 31)


class TestSbx(BaseDCPU16Test, unittest.TestCase):
    def test_Sbx(self):
        self.run_instructions([
            # set a, 20
            0x7c01, 20,
            # set b, 10
            0x7c21, 10,
            # add 0xffff, 0xffff (for EX):
            0x7fe2, 0xffff, 0xffff,
            # sbx a, b
            0x041b
        ])
        self.assertRegister("A", 11)


class TestSti(BaseDCPU16Test, unittest.TestCase):
    def test_sti(self):
        self.run_instructions([
            # set b, 10
            0x7c21, 10,
            # sti a, b
            0x041e
        ])
        self.assertRegister("A", 10)
        self.assertRegister("I", 1)
        self.assertRegister("J", 1)


class TestStd(BaseDCPU16Test, unittest.TestCase):
    def test_sti(self):
        self.run_instructions([
            # set b, 10
            0x7c21, 10,
            # sti a, b
            0x041f
        ])
        self.assertRegister("A", 10)
        self.assertRegister("I", 0xffff)
        self.assertRegister("J", 0xffff)
