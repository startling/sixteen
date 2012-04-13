; write the character at codepoint 0x3 and overwrite it with a `d`.

set [0x8000], 0b1111000000000011

set [0x8186], 0x3844
set [0x8187], 0xfF00


:loop set pc, loop
