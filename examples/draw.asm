; Draw a character at an arbitrary position.

; ascii "#"
set a, 35
; initialize position as 0, 0
set Y, 5
set X, 5
jsr draw
sub PC, 1

; draw the thing that's in A at the coordinates in X and Y
:draw
; calculate the actual position
set B, Y
set c, x
mod c, 32
mul B, 32
add B, c
add B, 0x8000
set [B], A
set PC, POP
