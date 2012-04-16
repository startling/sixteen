# sixteen

This is a DCPU-16 emulator written in python. Exciting stuff.

Here's what we've got so far:

## a virtual machine 

I'm almost certain it's spec-complete. The VM itself isn't terribly interesting, by itself (except when it is), but it has nice bindings. You can subclass it and do just about anything. See sixteen-web, sixteen-debug, and dcpubot, below.

## a basic debugger

run it like this:

````sh
sixteen-debug examples/quick_example.bin
````

You can specify two different options: `--little`, which interprets the binary as little-endian, and `--hex`, which reads an ASCII hex dump with possible whitespace.

It'll step through the instructions, printing each one. You can either hit return to continue stepping through, or use one of these commands:

* `r` or `register`: print all of the registers; it can also take a single argument (e.g., `r A`) and print that single register.
* `d` or `dump` takes a single argument, a hex number, and prints the value of the memory at that location.
* `q` or `quit` ends the debugger.
* `s` or `dis` takes a single argument (an address) and disassembles the code there.
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

## sixteen-web

sixteen-web is a web frontend for the virtual machine. Run it like this:

````sh
sixteen-web --hex examples/vram.hex
````

Point your browser at `http://localhost:1268` and you'll see something like this:

![sixteen-web](https://github.com/startling/sixteen/blob/master/sixteen.png?raw=true)

sixteen-web supports keyboard input, colored output (obviously), and everything else I can think of. It'll also re-read the file everytime you hit refresh, so you don't need to kill the server. 

Some notes regarding performance:

* Under Cpython and Firefox, the backend is the limiting factor -- Firefox's CPU usage hovers around 20%, as does the backend (depending on the number of cycles per draw in sixteen/web/dcpu16.js), but things are kind of slow.
* All of sixteen runs under Pypy, and in that case the frontend is what limits us. I get less than 10% usage for Pypy and ~60% from firefox.
* There's some primitive loop detection going on that can detect infinite loops of the kind that are used where a halt would be, so CPU usage goes down once a program reaches that point.
* The web frontend stops asking for the backend to cycle when it loses focus, so it won't spin in the background. This is nice because it leaves the browser an illusion of responsiveness.

Notice that the backend hasn't been optimized very much -- it's on the to-do list. If you're good at javascript, I'd love for you to check out sixteen/web/dcpu16.js for glaring inefficiencies, too -- javascript isn't my native language.

Here's the `--help`:

````
usage: sixteen-web [-h] [--little] [--hex] file

Run a DCPU-16 binary, displaying the output on a local webserver.

positional arguments:
  file          The binary file to run.

optional arguments:
  -h, --help    show this help message and exit
  --little, -l  Denote that this file should be parsed as little-endian.
                (Default: big-endian).
  --hex         Denote that this file should be parsed as an ASCII hex dump.
                (Default: binary)
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

* fix the quirky parts of the parser
* optimize the javascript in sixteen-web; firebug says 40% of the time is spent drawing pixels.
* write nice editor commands for sixteen-asm, sixteen-dis, and sixteen-web
* more debugger commands (including error-catching in the debugger)
