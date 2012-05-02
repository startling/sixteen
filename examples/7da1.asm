; this is a killer; it writes all of the memory to 0x7da1
:loop set push, 0x7da1
set pc, loop
