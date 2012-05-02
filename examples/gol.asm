; rmmh
; Conway's Game of Life
; Renders a 64x64 field by writing characters
; on a 16x8 grid

:begin
; Initialize the screen
SET [0x8280], 0x4 ; red border color

; Set screen to the appropriate characters
SET A, 0xf000 ; white fg | black bg | char #
SET Y, 1
:loop_init
SET X, 8
ADD Y, 1
:loop_init_inner
SET I, Y ; I = Y*32 + X + 0x8000
SHL I, 5
ADD I, X
BOR I, 0x8000
SET [I], A
ADD A, 1
ADD X, 1
IFN X, 24
  SET PC, loop_init_inner
IFN Y, 9
  SET PC, loop_init

; The core loop iterates over cells in a boustrophedon
; pattern -- examining 2x8 groups at a time, since that's
; the dimensions of one word of a character font

; C -- address of current field (since it's double-buffered)
; A, B -- coordinates inside current group
; X, Y -- coordinates of the current cell
; Z -- number of live neighbors
; SP -- address of last half-character we modified
; J -- current half-character bitmap
;       we modify a character by doing SET PUSH, J

SET C, 0x1000 ; the live/dead cells are stored at 0x1000 and 0x2000

:loop_main
SET X, 64 ; cell coords
SET Y, 64
SET SP, 0x8280 ; half-character address

:loop_group
SET A, 0
SET J, 0
  :loop_a
  SET B, 0
    :loop_b
    ;IFE A, B
      XOR J, 1
    SHL J, 1
    ADD B, 1
    IFN B, 8
      SET PC, loop_b
  ADD A, 1
  IFN A, 2
    SET PC, loop_a
SET PUSH, J
IFG SP, 0x817f	; have we written the last character?
  SET PC, loop_group

:inf  SET PC, inf
