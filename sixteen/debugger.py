#!/usr/bin/env python
# -*- coding: utf-8 -*-

import readline
from functools import wraps
from sixteen.words import as_opcode
from sixteen.utilities import OpcodeError


class Debugger(object):
	outer_prompt = ">> "
	inner_prompt = ">>>> "
	error = "Error: "
	format = "%04x"
	quit = ("q", "quit")

	def __init__(self, cpu):
		"Given a cpu, initialize a Debugger."
		self.cpu = cpu
		self.commands = {
			"r": self.registers,
			"registers": self.registers,
			"d": self.dump,
			"dump": self.dump,
			"dr": self.dump_range,
			"dumprange": self.dump_range,
			"c": self.continue_until,
			"continue": self.continue_until,
			"until": self.until,
			"u": self.until,
			"jump": self.jump,
			"j": self.jump,
			"dis": self.dis,
			"s": self.dis,
		}

	def format_output(fn):
		"A decorator that nicely formats binary output."
		@wraps(fn)
		def formatted(self, *args, **kwargs):
			c = fn(self, *args, **kwargs)
			# if it's a dict, format it like "a: b"
			if getattr(c, "keys", None):
				return " ".join("%s: %04x" % rs for rs in c.items())
			# if it's an iterable, format each item and join them
			elif getattr(c, "__iter__", None):
				return " ".join(self.format % i for i in c)
			# if it's a single item, format it and return it
			else:
				return self.format % c
		return formatted

	def step(self):
		try:
			op, args = self.cpu.cycle()
			if len(args) == 1:
				(a,) = args
				return "%s %s" % (op, a.dis)
			elif len(args) == 2:
				a, b = args
				return "%s %s, %s" % (op, a.dis, b.dis)
			#TODO: make this show hex values, too.
		except OpcodeError as o:
			return self.error + str(o)

	@format_output
	def dump(self, address):
		return self.cpu.RAM[self.parse_number(address)]

	@format_output
	def dump_range(self, first, second):
		return self.cpu.RAM[self.parse_number(first):self.parse_number(second)+ 1]

	@format_output
	def registers(self, r=None):
		if r == None:
			return self.cpu.registers
		else:
			return self.cpu.registers[r]

	def continue_until(self, pc):
		"Continue until PC is at the greater than the given address."
		while True:
			if self.cpu.registers["PC"] > self.parse_number(pc):
				break
			print self.step()
		return "<<"

	def until(self, pc):
		"Continue until PC is exactly equal to the given address."
		while True:
			if self.cpu.registers["PC"] == self.parse_number(pc):
				break
			print self.step()
		return "<<"

	def parse_number(self, n):
		i = int(n, base=16)
		# % it, so that we don't under/overflow.
		return i % len(self.cpu.RAM)

	def dis(self, addr):
		"Given an address, disassemble the word there."
		word = self.cpu.RAM[self.parse_number(addr)]
		try:
			# parse the opcodes and values out of the word
			opcode, values = self.cpu.parse_instruction(word)
			# print each opcode and its arguments
			assembly = "%s %s" % (opcode, ", ".join([v.dis for v in values]))
		# if there's an OpcodeError, it's a DAT instruction.
		except OpcodeError:
			assembly = "DAT 0x%04x" % word
		return assembly

	def jump(self, pc):
		"Move the PC to a given address."
		address = self.parse_number(pc)
		before = self.format % self.cpu.registers["PC"]
		# subtract one, because the CPU preincremements
		self.cpu.registers["PC"] = address - 1
		after = self.format % self.cpu.registers["PC"] + 1
		return "[%s] -> [%s]" % (before, after)

	def run(self, i):
		"Given an input, parse it and run it, if applicable."
		inputs = i.split()
		command = self.commands.get(inputs[0])
		if command != None:
			try:
				print command(*inputs[1:])
			# ignore argument errors for now.
			except TypeError:
				pass

	def __call__(self):
		"Step through the CPU, outputting prompts and taking commands."
		while True:
			# print the instructions used
			print self.step()
			line_in = raw_input(self.outer_prompt).strip()
			if line_in in self.quit:
				break
			# if it's empty, just pass
			elif len(line_in) == 0:
				pass
			else:
				self.run(line_in)
				# if we're given one command, prompt for more
				while True:
					line_in = raw_input(self.inner_prompt).strip()
					if len(line_in) == 0 or line_in in self.quit:
						break
					else:
						self.run(line_in)


class ColoredDebugger(Debugger):
	"A subclass of Debugger with colored prompts."
	outer_prompt = "\x1b[32m>>\x1b[39m "
	inner_prompt = "\x1b[36m>>>>\x1b[39m "
	error = "\x1b[31mError:\x1b[39m "
