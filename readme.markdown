This is a DCPU-16 emulator written in python. After it's complete, I'm going to make sure it's all rpython and write a JIT using pypy. Exciting stuff.

Here's what we've got so far:

## a virtual machine for most of the spec

The last thing I'm having trouble with is getting IF\*'s to jump over all the words in a single instruction.

## a basic debugger

run it like this:

````sh
sixteen-debug examples/quick_example.bin
````

It'll step through the binary, printing each word it's using. You can either hit return to continue stepping through, or use one of these commands:

* `r` or `register`: print all of the registers; it can also take a single argument (e.g., `r A`) and print that single register.
* `d` or `dump` takes a single argument, a four-digit long hex number, and prints the value of the memory at that location.
* `q` or `quit` ends the debugger.
