#!/usr/bin/env python
# -*- coding: utf-8 -*-

import readline
from functools import wraps
from sixteen.words import as_opcode


class Debugger(object):
	outer_prompt = ">> "
	inner_prompt = ">>>> "
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
		op, args = self.cpu.cycle()
		if len(args) == 1:
			(a,) = args
			return "%s %s" % (op, a.dis)
		elif len(args) == 2:
			a, b = args
			return "%s %s, %s" % (op, a.dis, b.dis)
		#TODO: make this show hex values, too.

	@format_output
	def dump(self, address):
		return self.cpu.RAM[int(address, base=16)]

	@format_output
	def dump_range(self, first, second):
		return self.cpu.RAM[int(first, base=16):int(second, base=16) + 1]

	@format_output
	def registers(self, r=None):
		if r == None:
			return self.cpu.registers
		else:
			return self.cpu.registers[r]

	def continue_until(self, pc):
		"Continue until PC is at the greater than the given address."
		while True:
			if self.cpu.registers["PC"] > int(pc, base=16):
				break
			print self.step()
		return "<<"

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
