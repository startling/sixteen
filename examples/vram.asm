; basic memory-mapped output test
set [0x8000], 104
set [0x8001], 101
set [0x8002], 108
set [0x8003], 108
set [0x8004], 111
set [0x8005], 32
set [0x8006], 119
set [0x8007], 111
set [0x8008], 114
set [0x8009], 108
set [0x800a], 100

:loop set PC, loop
