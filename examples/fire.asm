; http://0x10co.de/uftic
; LOL I HAVE NO IDEA WHAT I'M DOING
; ONE DOES NOT SIMPLY ASSEMBLY

; No, but like seriously. This could be greatly
; optimized I'm sure. I'm still learning and 
; I just kinda threw it together. It's slow.

; Also note, I did absolutely nothing to prevent
; fire from "bleeding" from one side of the screen
; to the other. So sue me.


SET PC, begin

:fire_ptr dat 0xA001
:screen_width DAT 0x20
:screen_height DAT 0xD

; Description
;	- Move fire upwards and draw results to screen.
;	  Fire is calculated at each pixel by adding
;	  the strength of the three pixels below it,
;	  then dividing the result by 4.

;	  Fire data is stored in a buffer starting
;	  at fire_ptr. The values within the buffer
;	  represent the "strength" of the flame.

:begin
		SET J, [fire_ptr]
		SET I, [screen_height]
        SUB I, 1
        MUL I, [screen_width]
        SUB I, 1
:update
		JSR do_bottom
        
        SET A, 0xFFFF
        

:update_loop
        SET B, 0

        ADD J, A
        ADD J, [screen_width]
        ADD B, [J]
        SUB J, 1
        ADD B, [J]
        ADD J, 2
        ADD B, [J]
        SUB J, 1
        SUB J, [screen_width]
        DIV B, 4

        SET [J], B
        SUB J, A
        ADD A, 1

        JSR draw

        IFE A, I
            SET PC, update

        SET PC, update_loop


; Description
;	- Draw to a point on screen
; Input
;	A - Screen Position
;	B - Fire Strength
; Output
;  	None
:draw
        IFG B, 0x1800
            JSR draw1
        IFG B, 0xF00
            JSR draw2
        IFG B, 0x900
            JSR draw3
        IFG B, 0x700
            JSR draw4
        IFG B, 0x400
            JSR draw5
        IFG B, 0x200
            JSR draw6

        JSR draw7

        SET PC, POP
:draw1
        SET [0x8000+A], 0xEE40
        SET O, POP
        SET PC, POP
:draw2
        SET [0x8000+A], 0xCE2A
        SET O, POP
        SET PC, POP
:draw3
        SET [0x8000+A], 0xEC2A
        SET O, POP
        SET PC, POP
:draw4
        SET [0x8000+A], 0x4C2A
        SET O, POP
        SET PC, POP
:draw5
        SET [0x8000+A], 0xC42A
        SET O, POP
        SET PC, POP
:draw6
        SET [0x8000+A], 0x402A
        SET O, POP
        SET PC, POP
:draw7
        SET [0x8000+A], 0
        SET O, POP
        SET PC, POP



; Description
;	- Set data for bottom of screen based
; Input
;	None
; Output
;  	None
:do_bottom
        SET PUSH, X

        SET B, 0xFFFF
        
        ADD J, I
        ADD J, 1

:do_bottom_loop

        ADD B, 1

        IFE B, [screen_width]
            SET PC, do_bottom_end
        JSR rand


        SET X, 0x1000
        IFG A, 0xA000
            SET X, 0x5000

        ADD J, B
        SET [J], X
        SUB J, B

        SET PC, do_bottom_loop
:do_bottom_end
		SUB J, 1
        SUB J, I
        SET X, POP
        SET PC, POP


; (PRNG code from AtlasOS - Thanks, Plusmid!)
; Returns a randomized number in A
:rand
        MUL [entropy], 52265
        ADD [entropy], 135
        SET A, [entropy]
        SET PC, POP

; Takes a seed in A
:srand
	MUL A, 49763
	SHL A, 2
	XOR A, 1273
	SET [entropy], A
	SET PC, POP

:entropy dat 0xA000

