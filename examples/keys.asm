:start

set A, 0
set B, 0
set C, 0

:loop
jsr drawCursor

ife [0x9000+C], 0
	set pc, loop
ife [0x9000+C], 0x0008
	jsr Backspace
    
set B, [0x9000+C]
Bor B, 0xB000
set [0x8000+A], B

set [0x9000+C], 0
Add A, 1
Add C, 1
And c, 15
set pc, loop

:Backspace
set [0x8000+A], 0
ifn A, 0
	Sub A, 1
set [0x8000+A], 0
set [0x9000+C], 0
Add c, 1
and c, 15
set pc, loop

:drawCursor
set [0x8000+A], 0xB07c 
set pc, pop
