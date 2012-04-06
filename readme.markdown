This is a DCPU-16 emulator written in python. After it's complete, I'm going to make sure it's all rpython and write a JIT using pypy. Exciting stuff.

Here's what we've got so far:

## a virtual machine for most of the spec

The last thing I'm having trouble with is getting IF\*'s to jump over all the words in a single instruction.

## a basic debugger

run it like this:

````sh
sixteen-debug examples/quick_example.bin
````

You can specify two different options: "--little", which interprets the binary as little-endian, and "--hex", which reads an ASCII hex dump with possible whitespace.

It'll step through the instructions, printing one. You can either hit return to continue stepping through, or use one of these commands:

* `r` or `register`: print all of the registers; it can also take a single argument (e.g., `r A`) and print that single register.
* `d` or `dump` takes a single argument, a four-digit long hex number, and prints the value of the memory at that location.
* `q` or `quit` ends the debugger.

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

## installation

If you have pip, you can install it like this:

````sh
pip install git+git://github.com/startling/sixteen.git
````
