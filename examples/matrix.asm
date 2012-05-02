;you may need to fix colors if your emulator does
;some other scheme, search 0xF200 and 0x0200 and
;change those values.
;
;you can also adjust display_width and display_height
;if your emulator differs from 32x12.
;
; ~enjoy~
;
;(ps, feel free to create an optimized version)

:entrypoint
  set a, 12345 ;change me!
  jsr srand
  jsr clear_screen
  jsr init_leading
  jsr init_tail_length
  jsr init_speed
  set pc, main ;never returns

:display_width
  dat 32 ;max 32
:display_height 
  dat 12 ;max 16

:main
  set push, x
  set push, y
  set push, z
  set i, 0
  
:main_loop_start
  set x, 0
  add i, 1
  mod i, 40
  set pc, main_loop

:main_next
  add x, 1
  ife x, [display_width]
    set pc, main_loop_start

:main_loop
  set a, i
  mod a, [speed+x]
  ifn a, 0
    set pc, main_next

  ;clear tail
  set y, [leading+x]
  sub y, [tail_length+x]
  ifg y, 0x7FFF
    add y, [display_height]
  set c, 0x0020
  set b, y
  set a, x
  jsr set_vram
  
  ;unhighlight last character
  set y, [leading+x]
  sub y, 1
  ifg y, 0x7FFF
    add y, [display_height]
  set b, y
  set a, x
  jsr get_vram
  set c, a
  and c, 0x00FF
  bor c, 0xD000
  set b, y
  set a, x
  jsr set_vram
  
  ;draw leading
  jsr get_character
  set c, a
  bor c, 0x0200
  set b, [leading+x]
  set a, x
  jsr set_vram
  
  ;move ahead
  set a, [leading+x]
  add a, 1
  mod a, [display_height]
  set [leading+x], a

  set pc, main_next

:get_vram
  mul b, [display_width]
  add a, b
  add a, 0x8000
  set a, [a]
  set pc, pop

:set_vram
  mul b, [display_width]
  add a, b
  add a, 0x8000
  set [a], c
  set pc, pop

:leading
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
:leading_end

:tail_length
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
:tail_length_end

:speed
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
  dat 0, 0, 0, 0, 0, 0, 0, 0
:speed_end

:init_leading
  set push, i
  set push, y
  set y, [display_height]
  set i, leading
:init_leading_loop
  jsr rand
  mod a, y
  set [i], a
  add i, 1
  ifn i, leading_end
    set pc, init_leading_loop
  set y, pop
  set i, pop
  set pc, pop

:init_tail_length
  set push, i
  set push, y
  set y, [display_height]
  div y, 3
  set i, tail_length
:init_tail_length_loop
  jsr rand
  mod a, y
  add a, 2
  set [i], a
  add i, 1
  ifn i, tail_length_end
    set pc, init_tail_length_loop
  set y, pop
  set i, pop
  set pc, pop

:init_speed
  set push, i
  set i, speed
:init_speed_loop
  jsr rand
  mod a, 35
  add a, 5
  set [i], a
  add i, 1
  ifn i, speed_end
    set pc, init_speed_loop
  set i, pop
  set pc, pop

:srand
  set [rand_seed], a
  set pc, pop

:rand
	set a, [rand_seed]
	mul a, 0x7C4D
	add a, 0x3619
	set b, rand_seed
	set [b], a
	set pc, pop
:rand_seed
	dat 0x5555

:get_character
  jsr rand
  mod a, 10
  set b, [get_character_table+a]
  set pc, b
:get_character_table
  dat get_character_number
  dat get_character_number
  dat get_character_number
  dat get_character_lower
  dat get_character_lower
  dat get_character_upper
  dat get_character_upper
  dat get_character_special_1
  dat get_character_special_2
  dat get_character_special_3
:get_character_number
  jsr rand
  mod a, 10
  add a, 0x30
  set pc, pop
:get_character_lower
  jsr rand
  mod a, 27
  add a, 0x61
  set pc, pop
:get_character_upper
  jsr rand
  mod a, 27
  add a, 0x41
  set pc, pop
:get_character_special_1
  jsr rand
  mod a, 0x0F
  add a, 0x21
  set pc, pop
:get_character_special_2
  jsr rand
  mod a, 0x05
  add a, 0x5B
  set pc, pop
:get_character_special_3
  jsr rand
  mod a, 0x04
  add a, 0x7B
  set pc, pop

:clear_screen
	set push, j
	set j, sp
	set sp, 0x8200
:clear_screen_loop
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  set push, 0x20
  ifn 0x8000, sp
    set pc, clear_screen_loop
  set sp, j
  set j, pop
  set pc, pop


