# sixteen

This is a DCPU-16 emulator written in python. After it's complete, I'm going to make sure it's all rpython and write a JIT using pypy. Exciting stuff.

Here's what we've got so far:

## a virtual machine 

I *think* it's spec-complete. Anyway, it's main use is the debugger, because we don't have any IO methods yet. I'll implement memory-mapping soon, too, but none of the spec uses it yet.

## a basic debugger

run it like this:

````sh
sixteen-debug examples/quick_example.bin
````

You can specify two different options: `--little`, which interprets the binary as little-endian, and `--hex`, which reads an ASCII hex dump with possible whitespace.

It'll step through the instructions, printing each one. You can either hit return to continue stepping through, or use one of these commands:

* `r` or `register`: print all of the registers; it can also take a single argument (e.g., `r A`) and print that single register.
* `d` or `dump` takes a single argument, a four-digit long hex number, and prints the value of the memory at that location.
* `q` or `quit` ends the debugger.
* `dr` or `dumprange`, which takes to address and dumps them and everything between them.
* `c` or `continue` takes an address and continues until the program counter is greater than that address.
* `u` or `until` takes an address and continues until the program counter is exactly equal to that address. Note that this is liable to spin forever, if you pick an address that's in the middle of an instruction or that doesn't get pointed to ever.
* `j` or `jump` moves the PC to a given address. Note that this can lead to nonsensical execution (inlcuding, possibly, an error) because not every address is the start of an instruction.

It also uses GNU Readline line-editing, so you can scroll through history.

Here's what a session looks like:

````
SET A, 0x0030
>> registers
A: 0030 C: 0000 B: 0000 I: 0000 J: 0000 O: 0000 PC: 0002 SP: ffff Y: 0000 X: 0000 Z: 0000
>>>> 
SET [0x1000], 0x0020
>> 
SUB A, [0x1000]
>> 
IFN A, 0x0010
>> registers
A: 0010 C: 0000 B: 0000 I: 0000 J: 0000 O: 0000 PC: 0009 SP: ffff Y: 0000 X: 0000 Z: 0000
>>>> 
>> quit
````

## sixteen-curses

This uses the DCPU16 vm and memory-mapped output with curses. The spec is kind of fuzzy at the moment; colors, for example, were deliberately excluded.

run it like this:

````sh
sixteen-curses --hex examples/vram.hex
````

When you're satisfied, `ctrl-c` quits and dumps all of the registers. It takes the `--hex` and `--litle` options, just like everything else, and a bunch of other things besides.

Here's the complete `--help`:

````
usage: sixteen-curses [-h] [--little] [--hex] [--step] [--quit] [--no-dump]
                      file

Run a DCPU-16 binary, using curses to display output.

positional arguments:
  file          The binary file to step through.

optional arguments:
  -h, --help    show this help message and exit
  --little, -l  Denote that this file should be parsed as little-endian.
                (Default: big-endian).
  --hex         Denote that this file should be parsed as an ASCII hex dump.
                (Default: binary)
  --step        Wait for a keypress after every instruction.
  --quit        Run until you press q.
  --no-dump     Don't dump the registers afterwards.
````

## an assembler!

run it like this:

````sh
sixteen-asm examples/quick_example.hex
````

It can take `--hex` (to output an ASCII hex dump) and `--little` (to output little-endian binary), too.

It supports all the ordinary opcodes, plus the pseudo-intructions `dat` and `jmp` and labels. Labels can be used like `label` where any value would go, or `[label]` (to use it as a pointer), or `[label + register]`. String literals can be used with `dat`, but there are a few quirks involved; namely, they can't contain spaces or commas. They *can* contain escaped quotes though.

Aditionally, I want to do something more with debugging symbols. Watch this space.

## a disassembler

run it like this:

````sh
sixteen-dis examples/quick_example.bin
````

Like sixteen-debug, you can run it with `--little` or `--hex`.


## dcpubot

This is an irc bot that assembles and runs (a subset of) dcpu-16 assembly. Run it like this:

````sh
dcpubot irc.example.com "#channel"
````

When you're in the same channel as it, you can issue it commands like so:

````
03:08 < startling> dcpubot: set a, 0xbeef / set b, 0xabcd / set c, 0xdeed
````

And it'll reply with something like...

````
03:08 < dcpubot> startling: 7c01 beef 7c11 abcd 7c21 deed -> A: beef C: deed B: abcd PC: 0007 (6)
````

That is, a hex dump of the assembled code, a dump of all the non-zero registers, and a word count.

He hangs out on #0x10c-dev, so be sure to stop by and say hi.


## installation

If you have pip, you can install it like this:

````sh
pip install git+git://github.com/startling/sixteen.git
````

## up next:

* a web frontend for local and remote use
* fix the quirky parts of the parser
* speculative input
* a raw terminal mode frontend (because curses sucks)
* more debugger commands (including error-catching in the debugger)
