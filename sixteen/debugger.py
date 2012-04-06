#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
		c = self.cpu.cycle()
		if len(c) == 2:
			name, a = c
			return "%s %s" % (name, a.dis)
		elif len(c) == 3:
			name, a, b = c
			return "%s %s %s" % (name, a.dis, b.dis)
		#TODO: make this show hex values, too.

	@format_output
	def dump(self, address):
		return self.cpu.RAM[int(address, base=16)]

	@format_output
	def registers(self, r=None):
		if r == None:
			return self.cpu.registers
		else:
			return self.cpu.registers[r]

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
