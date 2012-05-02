;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;                THY DUNGEONMAN
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;
;; Set up some core values that are only initialized on game start
SET [return_value], 0
SET [backlink], 0
SET [keyboard_mode], 0

;;;;;;;;;;;;;;;;;;
;; Skip down to the splash screen draw code, which inits wraps back around to
;; keyboard_hang
SET PC, draw_splash_screen

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; This is the main loop of the program- D16Stud only has a 1-word keyboard buffer
;; rather than the rotating 16-word buffer some have.
:keyboard_hang
        ;Keep checking 0x9000 for keyboard activity- loop until we get some
	SET B, [0x9000]
        SET A, [keyboard_mode]

        ;keyboard mode 3 should just hang permanently
        IFE A, 3
            SET PC, keyboard_hang

        ;keyboard mode 1 is terminal mode, so animate the blinking cursor
        IFE A, 1
            JSR terminal_cursor_blink

        ;No keyboard activity, keep looping
        IFE B, 0
            SET PC, keyboard_hang

        ;Clear the word to make room for new keystrokes
        SET [0x9000], 0

        ;Get the current keyboard state- if we're waiting for any key, then
        ;start a new game once someone presses a key
        IFE A, 0
            SET PC, new_game

        ;Convert all lower-case letters to upper-case
        ;We only care about alphabetic chars, spaces, enters, and backspaces
        ;at this point, so no need to be careful
        IFG B, 0x60
            SUB B, 0x20

        ;If/else - either process endgame "[Y/N]" or terminal typing
        IFE A, 1
            SET PC, keyboard_terminal
        SET PC, keyboard_endgame

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; The keyboard terminal mode takes in alphabetical keys and backspaces to
;; edit the current command buffer, and then pressing the enter key kicks off
;; a whole parse process that ends with the drawing of the next screen and
;; a return to the keyboard_hang
:keyboard_terminal
        ;Handle the backspace key
        IFE B, 0x08
            SET PC, terminal_backspace
        ;Handle the enter key
        IFE B, 0x0A
            SET PC, parse_terminal
        ;Handle the space key
        IFE B, 0x20
            SET PC, terminal_key
        ;Skip key if not alphabetic
        IFG 0x41, B
            SET PC, keyboard_hang
        IFG B, 0x5A
            SET PC, keyboard_hang
        ;Handle any alphabetic key
        SET PC, terminal_key
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; They keyboard endgame mode just sits until the player presses the Y/y key
;; and then begins a new game
:keyboard_endgame
        ;[Y/N] is misleading- we actually sit at the screen until the
        ;player types Y.  Then we start a new game
        IFE B, 0x59
            SET PC, new_game
        SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Terminal mode handler for the backspace key- eliminates the last char from
;; the command buffer
:terminal_backspace
        SET X, [command_length]

        IFE X, 0
           SET PC, keyboard_hang

        SET Y, command_buffer
        ADD Y, X
        SET [Y], 0

        SET Y, 0x81C3
        ADD Y, X
        SET [Y], 0
        SUB Y, 1
        SET [Y], [cursor_color]

        SUB X, 1
        SET [command_length], X

        SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Terminal mode handler for alphabetic keys- adds new char to the command
;; buffer
:terminal_key
        SET X, [command_length]

        IFE X, 26
            SET PC, keyboard_hang

        SET Y, command_buffer
        ADD Y, X
        SET [Y], B

        BOR B, 0x2000
        SET Y, 0x81C3
        ADD Y, X
        SET [Y], B
        ADD Y, 1
        SET [Y], [cursor_color]

        ADD X, 1
        SET [command_length], X

        SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Runs each keyboard tick - every 5000th run, toggles the terminal cursor color
:terminal_cursor_blink
        ;Decrement the cycles until next color toggle
        SUB [cursor_blink_loops], 1

        ;Wait until we hit 0
        IFG [cursor_blink_loops], 0
           SET PC, POP
        SET [cursor_blink_loops], 5000

        ;Once 0 - we need to toggle color and then replace
        ;the color in the terminal
        XOR [cursor_color], 0x200
        SET X, 0x81C3
        ADD X, [command_length]
        SET [X], [cursor_color]
        SET PC, POP

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Resets the game state - runs at the beginning of each new game
:reset_game
           SET [score], 0
           SET [current_room], 0
           SET [yondungeon_state], 0
           SET [escarpment_state], 0
           SET [getyeflask_attempts], 0

           SET PC, POP

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Initialize the command buffer and draw the command prompt.  Runs once
;; as a new screen is being drawn if it has terminal input.
:setup_terminal
           ;What wouldst thou deau?
           JSR start_proc
           SET X, 1
           SET Y, 0x0D
           SET I, 0x1E
           SET J, 0x0D
           SET Z, txt_prompt_line
           SET PUSH, write_text_nowrap
           JSR call_proc

           ;Draw prompt carot
           SET A, [txt_prompt_carot]
           BOR A, 0x2000
           SET [0x81C1], A

           ;Put a colored block (cursor) at the beginning of the command display
           SET [0x81C3], 0x0200

           ;Set length of typed command to 0
           SET [command_length], 0
           ;Set cycles until next cursor color toggle to 5000
           SET [cursor_blink_loops], 5000
           ;Set current cursor color to white
           SET [cursor_color], 0x0200
           ;Set the 26-char command buffer to all-0's
           SET I, command_buffer
           SET J, I
           ADD J, 27
:pvt_setup_terminal_loop
           IFE I, J
               SET PC, return
           SET [I], 0
           ADD I, 1
           SET PC, pvt_setup_terminal_loop

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; All terminal parsing methods- these methods begin with parse_terminal, which
;; is run when a user presses the ENTER key in a terminal display.  The
;; execution filters down through the various parsing method.  This execution
;; ends when being shunted to a screen-drawing method and then redirected back
;; to the keyboard hang.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Master method- identifies the core command used and passes commands with
;; targets on to the subparsers
:parse_terminal
           SET A, command_buffer

           ;Typed "HELP"
           JSR start_proc
           SET B, txt_cmd_help
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_current_room

           ;Typed "HELPETH"
           JSR start_proc
           SET B, txt_cmd_helpeth
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_current_room

           ;Typed "LOOK"
           JSR start_proc
           SET B, txt_cmd_look_noparams
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_current_room

           ;Typed "LOOK ___"
           JSR start_proc
           SET B, txt_cmd_look
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_look

           ;Typed "DIE"
           JSR start_proc
           SET B, txt_cmd_die
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, complete_game_die

           ;Typed "DANCE"
           JSR start_proc
           SET B, txt_cmd_dance
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_dance

           ;Typed "SMELL"
           JSR start_proc
           SET B, txt_cmd_smell
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_smell

           ;Typed "SNIFF"
           JSR start_proc
           SET B, txt_cmd_sniff
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_smell

           ;Typed "GET DAGGER"
           JSR start_proc
           SET B, txt_cmd_get_dagger
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_get_dagger

           ;Typed "GET YE ___"
           JSR start_proc
           SET B, txt_cmd_get_ye
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_get_ye

           ;Typed "GET YON ___"
           JSR start_proc
           SET B, txt_cmd_get_yon
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_get_yon

           ;Typed "GET ___"
           JSR start_proc
           SET B, txt_cmd_get
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_get

           ;Typed "TAKE YE ___"
           JSR start_proc
           SET B, txt_cmd_take_ye
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_take_ye

           ;Typed "TAKE YON ___"
           JSR start_proc
           SET B, txt_cmd_take_yon
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_take_yon

           ;Typed "TAKE ___"
           JSR start_proc
           SET B, txt_cmd_take
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_take

           ;Typed "GO ___"
           JSR start_proc
           SET B, txt_cmd_go
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_go

           ;Typed "TALK ___"
           JSR start_proc
           SET B, txt_cmd_talk
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_talk

           ;Typed "GIVE ___"
           JSR start_proc
           SET B, txt_cmd_give
           SET PUSH, starts_with
           JSR call_proc

           IFN [return_value], 0
               SET PC, parse_give

           SET PC, parse_huh

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; "LOOK ___" - parses direct object and routes
:parse_look
           ;We increment the command buffer pointer to isolate just the
           ;target text
           ADD A, 5

           IFE [current_room], 0
               SET PC, pvt_parse_look_yondungeon
           IFE [current_room], 1
               SET PC, pvt_parse_look_parapets
           IFE [current_room], 2
               SET PC, pvt_parse_look_escarpment
           IFE [current_room], 3
               SET PC, pvt_parse_look_dennis
:pvt_parse_look_yondungeon
           ;LOOK SCROLL
           JSR start_proc
           SET B, txt_dobj_scroll
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_scroll

           ;LOOK FLASK
           JSR start_proc
           SET B, txt_dobj_flask
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_flask

           SET PC, parse_look_huh
:pvt_parse_look_parapets
           ;LOOK ROPE
           JSR start_proc
           SET B, txt_dobj_rope
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_rope

           ;LOOK PARAPETS
           JSR start_proc
           SET B, txt_dobj_parapets
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_parapets

           SET PC, parse_look_huh
:pvt_parse_look_escarpment
           ;LOOK TRINKET
           JSR start_proc
           SET B, txt_dobj_trinket
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_trinket

           SET PC, parse_look_huh
:pvt_parse_look_dennis
           ;LOOK DENNIS
           JSR start_proc
           SET B, txt_dobj_dennis
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_dennis

           ;LOOK JIMBERJAM
           JSR start_proc
           SET B, txt_dobj_jimberjam
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_jimberjam
:parse_look_huh
           SET PC, draw_look_huh

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Various methods for parsing the different forms of get/take. We add to A
;; because A is currently pointing to the command string, so we increment it
;; until just the direct object is isolated
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;"GET YE ___"
:parse_get_ye
           ADD A, 7
           SET PC, parse_get_all
;"GET YON ___"
:parse_get_yon
;"TAKE YE ___"
:parse_take_ye
           ADD A, 8
           SET PC, parse_get_all
;"GET ___"
:parse_get
           ADD A, 4
           SET PC, parse_get_all
;"TAKE YON ___"
:parse_take_yon
           ADD A, 9
           SET PC, parse_get_all
;"TAKE ___"
:parse_take
           ADD A, 5
;Master method used by all forms of get/take
:parse_get_all

           IFE [current_room], 0
               SET PC, pvt_parse_get_yondungeon
           IFE [current_room], 1
               SET PC, pvt_parse_get_parapets
           IFE [current_room], 2
               SET PC, pvt_parse_get_escarpment
           SET PC, parse_get_huh
:pvt_parse_get_yondungeon
           ;GET YE SCROLL
           JSR start_proc
           SET B, txt_dobj_scroll
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_get_scroll

           ;GET YE FLASK
           JSR start_proc
           SET B, txt_dobj_flask
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_get_flask

           SET PC, parse_get_huh
:pvt_parse_get_parapets
           ;GET YE ROPE
           JSR start_proc
           SET B, txt_dobj_rope
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, complete_game_rope

           SET PC, parse_get_huh
:pvt_parse_get_escarpment
           ;GET YE TRINKET
           JSR start_proc
           SET B, txt_dobj_trinket
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_get_trinket
:parse_get_huh
           SET PC, draw_get_huh

;"GO ___" - parses exits and whatnot
:parse_go
           ADD A, 3

           ;Get exit from pvt_match_exits
           JSR pvt_match_exits

           IFN X, 0
               SET PC,X
           SET PC, draw_go_huh

;"TALK ___"
:parse_talk
           ADD A, 5

           ;Talk only ever works if you're in Dennis room
           IFN [current_room], 3
               SET PC, parse_talk_huh

           ;TALK DENNIS
           JSR start_proc
           SET B, txt_dobj_dennis
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, draw_talk_dennis
:parse_talk_huh
           SET PC, draw_talk_huh

;"GIVE ___"
:parse_give
           ADD A, 5

           ;Give only ever works if you're in Dennis room
           IFN [current_room], 3
               SET PC, draw_give_huh

           ;also you need to have the trinket
           IFE [escarpment_state], 0
               SET PC, draw_give_huh

           ;GIVE TRINKET
           JSR start_proc
           SET B, txt_dobj_trinket
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, complete_game_win

           ;GIVE TRINKET TO DENNIS
           JSR start_proc
           SET B, txt_trinket_to_dennis
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET PC, complete_game_win

           SET PC, draw_give_huh

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; This is last-chance parsing when we couldn't find a command we see if the
;; command actually matches a valid exit name otherwise, we print the Huh?
;; message
:parse_huh
           ;Get exit from pvt_match_exits
           JSR pvt_match_exits

           IFN X, 0
               SET PC,X
           SET PC, draw_final_huh

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Used by parse_huh and go ___ to try to parse exit code from the command
:pvt_match_exits
           SET X, 0
           SET C, [current_room]
           IFE C, 0
               SET PC, pvt_match_exits_yondungeon
           IFE C, 1
               SET PC, pvt_match_exits_parapets
           IFE C, 2
               SET PC, pvt_match_exits_escarpment
           IFE C, 3
               SET PC, pvt_match_exits_dennis
:pvt_match_exits_yondungeon
           JSR start_proc
           SET B, txt_dobj_north
           SET PUSH, string_equals
           JSR call_proc

           IFE [return_value], 0
               SET PC, pvt_match_exits_yondungeon_south

           SET X, draw_go_parapets
           SET PC, POP
:pvt_match_exits_yondungeon_south
           JSR start_proc
           SET B, txt_dobj_south
           SET PUSH, string_equals
           JSR call_proc

           IFE [return_value], 0
               SET PC, pvt_match_exits_yondungeon_dennis

           SET X, draw_go_escarpment
           SET PC, POP
:pvt_match_exits_yondungeon_dennis
           JSR start_proc
           SET B, txt_dobj_dennis
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET X, draw_go_dennis
           SET PC, POP
:pvt_match_exits_parapets
           JSR start_proc
           SET B, txt_dobj_south
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET X, draw_from_parapets
           SET PC, POP
:pvt_match_exits_escarpment
           JSR start_proc
           SET B, txt_dobj_north
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET X, draw_from_escarpment
           SET PC, POP
:pvt_match_exits_dennis
           JSR start_proc
           SET B, txt_dobj_not_dennis
           SET PUSH, string_equals
           JSR call_proc

           IFN [return_value], 0
               SET X, draw_from_dennis
           SET PC, POP

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; complete_game_die   - Reached when the player uses the "DIE" command
;; complete_game_rope  - Reached when the player tries to pick up the rope
;; complete_game_flask - Reached when the player tries to pick up ye flask 3
;;                       times
;;
;; All three of these failure states display a message, the player's score, and
;; a "Play Again? [Y/N]" message and switch the keyboard state to wait for plyaer
;; to hit Y.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
:complete_game_die
           SUB [score], 100
           SET B, txt_complete_die
           SET PC, complete_game_fail
:complete_game_rope
           SUB [score], 1
           SET B, txt_complete_rope
           SET PC, complete_game_fail
:complete_game_flask
           SUB [score], 1000
           SET B, txt_complete_flask
           SET PC, complete_game_fail
:complete_game_fail
 	;Clear the screen
	JSR start_proc
	SET PUSH, wipe_screen
	JSR call_proc

        ;Get pointers to some scratch space so we can do string manipulation
        SET A, scratch_space
        ADD A, 0x100
        SET C, A
        ADD C, 0x400

        ;Copy the fail message into scratch
        JSR start_proc
        SET PUSH, string_copy
        JSR call_proc

        ;Append "your score:"
        JSR start_proc
        SET B, txt_complete_score
        SET PUSH, string_concat
        JSR call_proc

        ;Generate score value
        JSR start_proc
        SET A, C
        SET B, [score]
        SET PUSH, string_itoa
        JSR call_proc
        SET C, [return_value]

        ;Append score value
        JSR start_proc
        SET B, C
        SET PUSH, string_concat
        JSR call_proc

        ;Append "Play again?"
        JSR start_proc
        SET B, txt_play_again
        SET PUSH, string_concat
        JSR call_proc

        ;Draw fail message
	JSR start_proc
	SET J, 0x0E
	SET I, 0x1E
	SET Y, 0x01
	SET X, 0x01
	SET Z, A
	SET PUSH, write_text
	JSR call_proc

        ;Set keyboard mode to Y/N
        SET [keyboard_mode], 2

        SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; This method generates a screen for players who complete the game- shows
;; the final score, and then locks the keyboard.
:complete_game_win
 	;Clear the screen
	JSR start_proc
	SET PUSH, wipe_screen
	JSR call_proc

        SET A, scratch_space
        ADD A, 0x100
        SET C, A
        ADD C, 0x400

        JSR start_proc
        SET B, txt_complete_win
        SET PUSH, string_copy
        JSR call_proc

        JSR start_proc
        SET B, txt_complete_score
        SET PUSH, string_concat
        JSR call_proc

        ;Generate score value
        JSR start_proc
        SET A, C
        SET B, [score]
        SET PUSH, string_itoa
        JSR call_proc
        SET C, [return_value]

        ;Append score value
        JSR start_proc
        SET B, C
        SET PUSH, string_concat
        JSR call_proc

        ;Draw win message
	JSR start_proc
	SET J, 0x0E
	SET I, 0x1E
	SET Y, 0x01
	SET X, 0x01
	SET Z, A
	SET PUSH, write_text
	JSR call_proc

        ;Lock keyboard
        SET [keyboard_mode], 3

        SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Each of the following methods are associated with a single game screen
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;THY DUNGEONMAN splash screen
:draw_splash_screen
	;Clear the screen
	JSR start_proc
	SET PUSH, wipe_screen
	JSR call_proc

        ;Thy Dungeonman
	JSR start_proc
	SET J, 0x01
	SET I, 0x1F
	SET Y, 1
	SET X, 9
	SET Z, txt_start_title
	SET PUSH, write_text_nowrap
	JSR call_proc

        ;Face Picture
	JSR start_proc
	SET X, 6
	SET Y, 4
	SET I, 0x0F
	SET J, 0x0A
	SET Z, txt_start_face
	SET PUSH, write_text_nowrap
	JSR call_proc

        ;Sword Picture
        JSR start_proc
        SET X, 0x14
        SET Y, 4
        SET I, 0x1B
        SET J, 0x0B
        SET Z, txt_start_sword
        SET PUSH, write_text_nowrap
        JSR call_proc

        ;Press any key
        JSR start_proc
        SET X, 0x01
        SET Y, 0x0E
        SET I, 0x1F
        SET J, 0x0E
        SET Z, txt_start_enter
        SET PUSH, write_text_nowrap
        JSR call_proc

        SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; New Game screen- set keyboard state to terminal, reset game state, and
;; display first room with intro text
:new_game
         SET [keyboard_mode], 1
         JSR reset_game

         JSR start_proc
         SET PUSH, wipe_screen
         JSR call_proc

         JSR start_proc
         SET X, 0x01
         SET Y, 0x01
         SET I, 0x1E
         SET J, 0x03
         SET Z, txt_start_intro
         SET PUSH, write_text_nowrap
         JSR call_proc

         JSR start_proc
         SET X, 0x01
         SET Y, 0x05
         SET I, 0x1E
         SET J, 0x0B
         SET Z, txt_mainroom_state1
         SET PUSH, write_text
         JSR call_proc

         JSR start_proc
         SET PUSH, setup_terminal
         JSR call_proc

         SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Method that draws the current room in response to "look" or "help"
:draw_current_room
         JSR start_proc
         SET PUSH, wipe_screen
         JSR call_proc

         IFE [current_room], 0
             SET PC, draw_current_room_yondungeon
         IFE [current_room], 1
             SET PC, draw_current_room_parapets
         IFE [current_room], 2
             SET PC, draw_current_room_escarpment
         IFE [current_room], 3
             SET PC, draw_current_room_dennis
:draw_current_room_yondungeon
         IFE [yondungeon_state], 0
             SET PC, pvt_draw_current_room_withscroll

         SET A, scratch_space
         ADD A, 100
         JSR start_proc
         SET B, txt_mainroom_state2
         SET PUSH, string_copy
         JSR call_proc

         IFE [yondungeon_state], 1
             SET PC, pvt_current_room_yondungeon_final

         JSR start_proc
         SET B, txt_mainroom_definitely_no_scroll
         SET PUSH, string_concat
         JSR call_proc
:pvt_current_room_yondungeon_final
         ;Draw Yon Dungeon with no scroll
         SET Z, A
         SET PC, simple_draw
:pvt_draw_current_room_withscroll
         ;Draw Yon Dungeon with scroll
         SET Z, txt_mainroom_state1
         SET PC, simple_draw
:draw_current_room_parapets
         ;Draw Parapets
         SET Z, txt_northroom_examine
         SET PC, simple_draw
:draw_current_room_escarpment
         IFE [escarpment_state], 0
             SET PC, pvt_draw_current_room_withtrinket

         SET A, scratch_space
         ADD A, 100
         JSR start_proc
         SET B, txt_southroom_state2_examine
         SET PUSH, string_copy
         JSR call_proc

         IFE [escarpment_state], 1
             SET PC, pvt_current_room_escarpment_final

         JSR start_proc
         SET B, txt_southroom_definitely_no_trinket
         SET PUSH, string_concat
         JSR call_proc

:pvt_current_room_escarpment_final
         ;Draw Escarpment without trinket
         SET Z, A
         SET PC, simple_draw
:pvt_draw_current_room_withtrinket
         ;Draw Escarpment without trinket
         SET Z, txt_southroom_state1_examine
         SET PC, simple_draw
:draw_current_room_dennis
         ;Draw Dennis
         SET Z, txt_dennis
         SET PC, simple_draw


;Draw helper for "DANCE" command
:draw_dance
         SET Z, txt_command_dance
         SET PC, simple_draw

;Draw helper for "SMELL" command
:draw_smell
         SET Z, txt_command_smell
         SET PC, simple_draw

;Draw helper for "GET DAGGER" command
:draw_get_dagger
         ADD [score], 25
         SET Z, txt_get_dagger
         SET PC, simple_draw

;Draw helper for "LOOK SCROLL" command
:draw_scroll
         IFN [yondungeon_state], 0
             SET PC, draw_scroll_taken
         SET Z, txt_look_scroll_state1
         SET PC, simple_draw
:draw_scroll_taken
         SET Z, txt_look_scroll_state2
         SET PC, simple_draw

;Draw helper for "LOOK FLASK" command
:draw_flask
         SET Z, txt_look_flask
         SET PC, simple_draw

;Draw helper for "LOOK ROPE" command
:draw_rope
         SET Z, txt_look_rope
         SET PC, simple_draw

;Draw helper for "LOOK PARAPETS" command
:draw_parapets
         SET Z, txt_look_parapets
         SET PC, simple_draw

;Draw helper for "LOOK TRINKET" command
:draw_trinket
         IFN [escarpment_state], 0
             SET PC, draw_trinket_taken
         SET Z, txt_look_trinket_state1
         SET PC, simple_draw
:draw_trinket_taken
         SET Z, txt_look_trinket_state2
         SET PC, simple_draw

;Draw helper for "LOOK DENNIS" command
:draw_dennis
         SET Z, txt_look_dennis
         SET PC, simple_draw

;Draw helper for "LOOK JIMBERJAM" command
:draw_jimberjam
         SET Z, txt_look_jimberjam
         SET PC, simple_draw

;Draw helper for "LOOK ___" fallback text
:draw_look_huh
         SET Z, txt_look_huh
         SET PC, simple_draw

;Draw helper for "GET SCROLL" command
:draw_get_scroll
         IFN [yondungeon_state], 0
             SET PC, draw_get_scroll_taken
         ADD [score], 2
         SET [yondungeon_state], 1
         SET Z, txt_get_scroll_state1
         SET PC, simple_draw
:draw_get_scroll_taken
         SUB [score], 1
         SET [yondungeon_state], 2
         SET Z, txt_get_scroll_state2
         SET PC, simple_draw

;Draw helper for "GET TRINKET" command
:draw_get_trinket
         IFN [escarpment_state], 0
             SET PC, draw_get_trinket_taken
         ADD [score], 2
         SET [escarpment_state], 1
         SET Z, txt_get_trinket_state1
         SET PC, simple_draw
:draw_get_trinket_taken
         SUB [score], 1
         SET [escarpment_state], 2
         SET Z, txt_get_trinket_state2
         SET PC, simple_draw

;Draw helper for "GET FLASK" command
:draw_get_flask
         ADD [getyeflask_attempts], 1
         IFE [getyeflask_attempts], 3
             SET PC, complete_game_flask
         ADD [score], 1
         SET Z, txt_get_flask
         SET PC, simple_draw

;Draw helper for "GET YE ___" fallback text
:draw_get_huh
         SET Z, txt_get_huh
         SET PC, simple_draw

;Draw helper for "GO ___" fallback text
:draw_go_huh
         SET Z, txt_go_huh
         SET PC, simple_draw

;Draw helper for "TALK DENNIS" command
:draw_talk_dennis
         SET Z, txt_talk_dennis
         SET PC, simple_draw

;Draw helper for "TALK ___" fallback text
:draw_talk_huh
         SET C, A

         ADD A, 1
         JSR start_proc
         SET PUSH, string_make_lower
         JSR call_proc

         SET A, scratch_space
         ADD A, 100

         JSR start_proc
         SET B, txt_talk_huh1
         SET PUSH, string_copy
         JSR call_proc

         JSR start_proc
         SET B, C
         SET PUSH, string_concat
         JSR call_proc

         JSR start_proc
         SET B, txt_talk_huh2
         SET PUSH, string_concat
         JSR call_proc

         SET Z, A
         SET PC, simple_draw

;Draw helper for "GIVE ___" fallback text
:draw_give_huh
         JSR start_proc
         SET PUSH, string_make_lower
         JSR call_proc

         SET C, A
         SET A, scratch_space
         ADD A, 100

         JSR start_proc
         SET B, txt_give_huh1
         SET PUSH, string_copy
         JSR call_proc

         JSR start_proc
         SET B, C
         SET PUSH, string_concat
         JSR call_proc

         JSR start_proc
         SET B, txt_give_huh2
         SET PUSH, string_concat
         JSR call_proc

         SET Z, A
         SET PC, simple_draw

;Draw helper for final fallback text when nothing parses
:draw_final_huh
         SET Z, txt_final_huh
         SET PC, simple_draw

;Draw helper for "GO NORTH" from yon dungeon
:draw_go_parapets
         SET [current_room], 1
         SET Z, txt_northroom
         SET PC, simple_draw

;Draw helper from "GO SOUTH" from yon dungeon
:draw_go_escarpment
         SET [current_room], 2
         SET Z, txt_southroom
         SET PC, simple_draw

;Draw helper from "GO DENNIS" from yon dungeon
:draw_go_dennis
         SET [current_room], 3
         SET Z, txt_dennis
         SET PC, simple_draw

;Draw helper from "GO SOUTH" in parapets
:draw_from_parapets
         SET B, txt_mainroom_fromnorth
         SET PC, draw_go_yondungeon
;Draw helper from "GO NORTH" in escarpment
:draw_from_escarpment
         SET B, txt_mainroom_fromsouth
         SET PC, draw_go_yondungeon
;Draw helper from "GO NOT DENNIS" in dennis
:draw_from_dennis
         SET B, txt_mainroom_fromdennis
         SET PC, draw_go_yondungeon
;All 3 to-yon-dungeon exits lead to this code
:draw_go_yondungeon
         SET [current_room], 0

         JSR start_proc
         SET PUSH, wipe_screen
         JSR call_proc

         ;Set up scratch space- coming in to yon dungeon combines
         ;an exit-specific description with the standard room description
         SET A, scratch_space
         ADD A, 100

         ;Copy exit description
         JSR start_proc
         SET PUSH, string_copy
         JSR call_proc

         IFE [yondungeon_state], 0
             SET B, txt_mainroom_state1
         IFN [yondungeon_state], 0
             SET B, txt_mainroom_state2

         ;Concat room description
         JSR start_proc
         SET PUSH, string_concat
         JSR call_proc

         ;If the state is 2 we need to also concat a "no scroll here" message to the end
         IFN [yondungeon_state], 2
             SET PC, pvt_draw_go_yondungeon_final

         JSR start_proc
         SET B, txt_mainroom_definitely_no_scroll
         SET PUSH, string_concat
         JSR call_proc

;Draw the concatted description & then the terminal prompt
:pvt_draw_go_yondungeon_final
         JSR start_proc
         SET X, 1
         SET Y, 1
         SET I, 0x1E
         SET J, 0x0B
         SET Z, A
         SET PUSH, write_text
         JSR call_proc

         JSR start_proc
         SET PUSH, setup_terminal
         JSR call_proc

         SET PC, keyboard_hang


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Helper command for a screen that's just a simple message and a terminal at
;; the bottom.  Called by most draw helper methods above.
:simple_draw
         JSR start_proc
         SET PUSH, wipe_screen
         JSR call_proc

         JSR start_proc
         SET X, 1
         SET Y, 1
         SET I, 0x1E
         SET J, 0x0B
         SET PUSH, write_text
         JSR call_proc

         JSR start_proc
         SET PUSH, setup_terminal
         JSR call_proc

         SET PC, keyboard_hang

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Vox Technologie screen helpers
;; :wipe_screen - used to clear everything on the screen to black
;; :write_text - used to draw green text, word-wrapped properly, within the
;;               given rectangle
;; :write_text_nowrap - used to draw the green text in the given rectangle with
;;                      no special wrapping
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;Wipe the full screen with no exceptions
:wipe_screen
	SET I, 0
:pvt_wipe_line
	SET [0x8000+I], 0x00
	SET [0x8001+I], 0x00
	SET [0x8002+I], 0x00
	SET [0x8003+I], 0x00
	SET [0x8004+I], 0x00
	SET [0x8005+I], 0x00
	SET [0x8006+I], 0x00
	SET [0x8007+I], 0x00
	SET [0x8008+I], 0x00
	SET [0x8009+I], 0x00
	SET [0x800A+I], 0x00
	SET [0x800B+I], 0x00
	SET [0x800C+I], 0x00
	SET [0x800D+I], 0x00
	SET [0x800E+I], 0x00
	SET [0x800F+I], 0x00
	SET [0x8010+I], 0x00
	SET [0x8011+I], 0x00
	SET [0x8012+I], 0x00
	SET [0x8013+I], 0x00
	SET [0x8014+I], 0x00
	SET [0x8015+I], 0x00
	SET [0x8016+I], 0x00
	SET [0x8017+I], 0x00
	SET [0x8018+I], 0x00
	SET [0x8019+I], 0x00
	SET [0x801A+I], 0x00
	SET [0x801B+I], 0x00
	SET [0x801C+I], 0x00
	SET [0x801D+I], 0x00
	SET [0x801E+I], 0x00
	SET [0x801F+I], 0x00

	ADD I, 0x20

	IFG I, 0x1FF
	    SET PC, return
	SET PC, pvt_wipe_line

;Print text to the screen in the box indicated by the parameters
:write_text
	SET A, Y
        MUL A, 0x20
        ADD A, 0x8000
        SET B, A
        ADD A, X
        ADD B, I
        JSR pvt_write_findeol

:pvt_write_char
        IFE [Z], 0
            SET PC, return
        IFE [Z], 0x0A
            SET PC, pvt_write_newline
        IFE Z, [scratch_space]
            SET PC, pvt_write_line
        SET C, [Z]
        BOR C, 0x2000
        SET [A], C
        ADD A, 1
        ADD Z, 1
        IFG A, B
            SET PC, pvt_write_line
        SET PC, pvt_write_char

:pvt_write_newline
        ADD Z, 1
:pvt_write_line
        ADD Y, 1
        IFG Y, J
            SET PC, return
        ADD B, 0x20
        SET A, B
        SUB A, I
        ADD A, X
        JSR pvt_write_findeol
        SET PC, pvt_write_char
;Private segment that backtracks the end of line
;cursor to the end of the last word- used to wrap
;words
:pvt_write_findeol
        SET [scratch_space_1], A
        SET A, Z
        ADD A, 0x1E
:pvt_write_findeol_loop
        IFE [A], 0x20
            SET PC, pvt_write_findeol_end
        IFE [A], 0x0A
            SET PC, pvt_write_findeol_end
        IFE [A], 0x00
            SET PC, pvt_write_findeol_end
        SUB A, 1
        IFE A, Z
            SET PC, pvt_write_findeol_reset
        SET PC, pvt_write_findeol_loop
:pvt_write_findeol_reset
        SET A, Z
        ADD A, 0x20
:pvt_write_findeol_end
        SET [scratch_space], A
        SET A, [scratch_space_1]
        SET PC, POP

;As write_text above, but with NO wrapping-
;there is a noticeable delay between lines with wrapping
;which is fine when there's a purpose, but unwrapped
;text looks dumb with it
;Print text to the screen in the box indicated by the parameters
:write_text_nowrap
	SET A, Y
        MUL A, 0x20
        ADD A, 0x8000
        SET B, A
        ADD A, X
        ADD B, I

:pvt_write_nowrap_char
        IFE [Z], 0
            SET PC, return
        IFE [Z], 0x0A
            SET PC, pvt_write_nowrap_newline
        SET C, [Z]
        BOR C, 0x2000
        SET [A], C
        ADD A, 1
        ADD Z, 1
        IFG A, B
            SET PC, pvt_write_nowrap_line
        SET PC, pvt_write_nowrap_char

:pvt_write_nowrap_newline
        ADD Z, 1
:pvt_write_nowrap_line
        ADD Y, 1
        IFG Y, J
            SET PC, return
        ADD B, 0x20
        SET A, B
        SUB A, I
        ADD A, X
        SET PC, pvt_write_nowrap_char

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Vox Technologie String Helpers - several string operations
;;
;; :starts_with - returns true if the string at [A] begins with the string at
;;                [B]
;; :string_equals - tests equality between the strings at [A] and [B]
;; :string_copy - copies the string at [B] to the memory located at A
;; :string_concat - tacks the string at [B] to the end of the string at [A]
;; :string_length - returns the length of the string at [A]
;; :string_make_lower - Makes all upper-case characters at [A] be lower case
;; :string_itoa - turns the number B into a string and copies it into the
;;                32-byte buffer located at A.  Returns the pointer for the
;;                beginning of the final string.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;Some private segments used by starts_with and string_equals
:pvt_test_fail
        SET [return_value], 0
        SET PC, return
:pvt_test_success
        SET [return_value], 1
        SET PC, return

:starts_with
        IFE [B], 0
            SET PC, pvt_test_success
        IFN [A], [B]
            SET PC, pvt_test_fail
        ADD A, 1
        ADD B, 1
        SET PC, starts_with

:string_equals
        IFN [A], [B]
            SET PC, pvt_test_fail
        IFE [A], 0
            SET PC, pvt_test_success
        ADD A, 1
        ADD B, 1
        SET PC, string_equals

:string_copy
        SET [A], [B]
        IFE [B], 0
            SET PC, return
        ADD A, 1
        ADD B, 1
        SET PC, string_copy

:string_concat
        IFE [A], 0
            SET PC, string_copy
        ADD A, 1
        SET PC, string_concat

:string_length
        SET I, 0
        IFE [A], 0
            SET PC, pvt_string_length_end
        ADD A, 1
        ADD I, 1
        SET PC, string_length
:pvt_string_length_end
        SET [return_value], I
        SET PC, return

:string_make_lower
        IFE [A], 0
            SET PC, return
        IFG 0x41, [A]
            SET PC, pvt_string_make_lower_next
        IFG [A], 0x5A
            SET PC, pvt_string_make_lower_next
        ADD [A], 0x20
:pvt_string_make_lower_next
        ADD A, 1
        SET PC, string_make_lower

;Stick the text for the given numerical value
;at the given addres
:string_itoa
        SET C, A
        ADD C, 31
        SET [C], 0
        SUB C, 1

        ;Check for negative
        SET I, B
        AND I, 0x8000

        ;If negative, then negate B
        IFE I, 0
            SET PC, pvt_string_itoa_loop

        XOR B, 0xFFFF
        ADD B, 1

:pvt_string_itoa_loop
        IFE B, 0
            SET PC, pvt_string_itoa_done
        IFE C, A
            SET PC, pvt_string_itoa_done

        SET X, B
        MOD X, 10
        ADD X, 0x30
        SET [C], X
        SUB C, 1
        DIV B, 10
        SET PC, pvt_string_itoa_loop
:pvt_string_itoa_done
        IFE I, 0
            ADD C, 1
        IFN I, 0
            SET [C], 0x2D

        SET [return_value], C
        SET PC, return

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Vox Technologie Subroutine System
;;
;; :start_proc - should be called first with JSR - saves current state to stack
;; :call_proc - called when ready to execute, with JSR - saves backlink and
;;              calls code that was last saved to stack
;; :return    - called at end of subroutine with SET PC, return - reloads saved
;;              state and returns to backlink.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

:start_proc

	SET [vxtec_proc_scratch], POP
	SET PUSH, A
	SET PUSH, B
	SET PUSH, C
	SET PUSH, X
	SET PUSH, Y
	SET PUSH, Z
	SET PUSH, I
	SET PUSH, J
	SET PUSH, O
	SET PUSH, [backlink]
	SET PC, [vxtec_proc_scratch]

:call_proc
	SET [backlink], POP
	SET PC, POP

:return
	SET [vxtec_proc_scratch], [backlink]
	SET [backlink], POP
	SET O, POP
	SET J, POP
	SET I, POP
	SET Z, POP
	SET Y, POP
	SET X, POP
	SET C, POP
	SET B, POP
	SET A, POP
	SET PC, [vxtec_proc_scratch]


; Text resources
:txt_start_title
	DAT "Thy Dungeonman", 0x00

:txt_start_face
	DAT "/\\      /\\", "||/----\\||", "\\_------_/"," / o  o \\", 0x0A," /  ||  \\", 0x0A," / ---- \\", 0x0A," /\\/\\/\\/\\ ", 0x00

:txt_start_sword
	DAT "   /\\", 0x0A,"   ||", 0x0A,"   ||", 0x0A,"o__||__o"," \\----/", 0x0A,"   ||", 0x0A,"   oo", 0x00

:txt_start_enter
	DAT "Press key to enter yon Dungeon", 0x00

:txt_prompt_line
	DAT "What wouldst thou deau?", 0x00

:txt_prompt_carot
	DAT ">", 0x00

:txt_command_dance
	DAT "Thou shaketh it a little, and it feeleth all right.", 0x00

:txt_command_smell
	DAT "You smell a Wumpus.", 0x00

:txt_get_huh
	DAT "Thou cannotst get that. Quit making stuffeth up!", 0x00

:txt_go_huh
	DAT "Thou cannotst go there. Who do you think thou art? A magistrate?!", 0x00

:txt_look_huh
	DAT "It looketh pretty awesome.", 0x00

:txt_talk_huh1
	DAT "Who is \"", 0x00

:txt_talk_huh2
	DAT "\"? Your new boyfriend? Somebody from work you don't want me to meeteth?", 0x00

:txt_give_huh1
	DAT "Thou don'tst have a ",0x00

:txt_give_huh2
	DAT " to give. Go back to your tiny life.", 0x00

:txt_final_huh
	DAT "That does not computeth.  Type HELP is thou needs of it.", 0x00

:txt_get_dagger
	DAT "Yeah, okay.", 0x00

:txt_start_intro
	DAT "THY DUNGEONMAN", 0x0A, 0x0A, "YOU ARE THY DUNGEONMAN!", 0x00

:txt_mainroom_state1
	DAT "Ye find yeself in yon dungeon. Ye see a SCROLL. Behind ye scroll is a FLASK. Obvious exits are NORTH, SOUTH and DENNIS.", 0x00

:txt_mainroom_state2
	DAT "Ye find yeself in yon dungeon. Back yonder there is a FLASK. Obvious exits are NORTH, SOUTH, and DENNIS.", 0x00

:txt_mainroom_definitely_no_scroll
	DAT " There is definitely no YE SCROLL, so drop it.", 0x00

:txt_mainroom_fromnorth
	DAT "You go SOUTH back through yon corridor.", 0x0A, 0x00

:txt_mainroom_fromsouth
	DAT "You go NORTH.", 0x0A, 0x00

:txt_mainroom_fromdennis
	DAT "You go NOT DENNIS.", 0x0A, 0x00

:txt_northroom
	DAT "You go NORTH through yon corridor. You arrive at parapets. Ye see a ROPE. Obvious exits are SOUTH.", 0x00

:txt_northroom_examine
	DAT "Ye thou now be at parapets. Ye see a ROPE. Obvious exits are SOUTH.", 0x00

:txt_southroom
	DAT "You head south to an embankment. Or maybe a chasm. You can't decide which. Anyway, ye spies a TRINKET. Obvious exits are NORTH.", 0x00

:txt_southroom_state1_examine
	DAT "Ye stand yeself close to a yet-unnamed escarpment. Nonetheless, ye spies a TRINKET. Obvious exits are NORTH.", 0x00

:txt_southroom_state2_examine
	DAT "Ye stand high above a canyon-like depression. Obvious exits are NORTH.", 0x00

:txt_southroom_definitely_no_trinket
	DAT " I shouldn't have to tell ye there is no TRINKET.", 0x00

:txt_dennis
	DAT "Ye arrive at Dennis. He wears a sporty frock coat and a long jimberjam. He paces about nervously. Obvious exits are NOT DENNIS.", 0x00

:txt_get_scroll_state1
	DAT "Ye takes the SCROLL and reads of it. It doth say:", 0x0A, 0x0A,"BEWARE, READER OF YE SCROLL, DANGERS AWAIT TO THE -", 0x0A, 0x0A,"The SCROLL disappears in thy hands with ye olde ZAP!", 0x00

:txt_get_scroll_state2
	DAT "Ye doth suffer from memory loss. YE SCROLL is no more. Honestly.", 0x00

:txt_look_scroll_state1
	DAT "Parchment, definitely parchment. I'd recognize it anywhere.", 0x00

:txt_look_scroll_state2
	DAT "Ye seeth nothing wheretofore it went ZAP.", 0x00

:txt_get_flask
	DAT "Ye cannot get the FLASK. It is firmly bolted to a wall which is bolted to the rest of the dungeon which is probably bolted to a castle. Never you mind.", 0x00

:txt_look_flask
	DAT "Looks like you could quaff some serious mead out of that thing.", 0x00

:txt_look_parapets
	DAT "Well, they're parapets. This much we know for sure.", 0x00

:txt_look_rope
	DAT "It looks okay. You've seen better.", 0x00

:txt_look_trinket_state1
	DAT "Quit looking! Just get it already.", 0x00

:txt_look_trinket_state2
	DAT "Just a bulge in thou pouchel at thist point.", 0x00

:txt_get_trinket_state1
	DAT "Ye getsts yon TRINKET and discover it to be a bauble. You rejoice at your good fortune. You shove the TRINKET in your pouchel. It kinda hurts.", 0x00

:txt_get_trinket_state2
	DAT "Sigh. The trinket is in thou pouchel. Recallest thou?", 0x00

:txt_talk_dennis
	DAT "You engage Dennis in leisurely discussion. Ye learns that his jimberjam was purchased on sale at a discount market and that he enjoys pacing about nervously. You become bored and begin thinking about parapets.", 0x00

:txt_look_jimberjam
	DAT "Man, that art a nice jimberjam.", 0x00

:txt_look_dennis
	DAT "That jimberjam really majkes the outfit.", 0x00

:txt_complete_die
	DAT "That wasn't very smart.", 0x00

:txt_complete_flask
	DAT "Okay, okay. You unbolt yon FLASK and hold it aloft. A great shaking begins. The dungeon ceiling collapses down on you, crushing you in twain. Apparently, this was a load-bearing FLASK.", 0x00

:txt_complete_rope
	DAT "You attempt to take ye ROPE but alas it is enchanted! It glows a mustard red and smells like a public privy. The ROPE wraps round your neck and hangs you from the parapets. With your last breath, you wonder what parapets are. GAME OVER.", 0x00

:txt_complete_win
	DAT "A novel idea! You givst the TRINKET to Dennis and he happily agrees to tell you what parapets are. With this new knowledge, ye escapes from yon dungeon in order to search for new dungeons and remain...", 0x0A, 0x0A,"THY DUNGEONMAN!!", 0x0A,"You hath won! Congraturation!!", 0x00

:txt_complete_score
	DAT 0x0A, "Your score was: ", 0x00

:txt_play_again
	DAT 0x0A, 0x0A, "Play again? [Y/N]", 0x00

:txt_cmd_look
	DAT "LOOK ", 0x00

:txt_cmd_look_noparams
	DAT "LOOK", 0x00

:txt_cmd_help
	DAT "HELP", 0x00

:txt_cmd_helpeth
	DAT "HELPETH", 0x00

:txt_cmd_die
	DAT "DIE", 0x00

:txt_cmd_dance
	DAT "DANCE", 0x00

:txt_cmd_smell
	DAT "SMELL", 0x00

:txt_cmd_sniff
	DAT "SNIFF", 0x00

:txt_cmd_get_ye
	DAT "GET YE ", 0x00

:txt_cmd_get_yon
	DAT "GET YON ", 0x00

:txt_cmd_get_dagger
	DAT "GET DAGGER", 0x00

:txt_cmd_get
	DAT "GET ", 0x00

:txt_cmd_take_ye
	DAT "TAKE YE ", 0x00

:txt_cmd_take_yon
	DAT "TAKE YON ", 0x00

:txt_cmd_take
	DAT "TAKE ", 0x00

:txt_cmd_go
	DAT "GO ", 0x00

:txt_cmd_talk
	DAT "TALK ", 0x00

:txt_cmd_give
	DAT "GIVE ", 0x00

:txt_dobj_scroll
	DAT "SCROLL", 0x00

:txt_dobj_flask
	DAT "FLASK", 0x00

:txt_dobj_rope
	DAT "ROPE", 0x00

:txt_dobj_trinket
	DAT "TRINKET", 0x00

:txt_dobj_north
	DAT "NORTH", 0x00

:txt_dobj_south
	DAT "SOUTH", 0x00

:txt_dobj_dennis
	DAT "DENNIS", 0x00

:txt_dobj_not_dennis
	DAT "NOT DENNIS", 0x00

:txt_dobj_parapets
	DAT "PARAPETS", 0x00

:txt_dobj_jimberjam
	DAT "JIMBERJAM", 0x00

:txt_trinket_to_dennis
	DAT "TRINKET TO DENNIS", 0x00

;Memory used in-game

;Storage spot for procedures with a return value
:return_value
	DAT 0x00

;No BL register, so we store backlinks here
:backlink
	DAT 0x00

;Keyboard mode
; 0 - Any key to continue
; 1 - Terminal type
; 2 - Y to continue
; 3 - Locked (after victory)
:keyboard_mode
	DAT 0x00

;Number of keyboard driver iterations until next
;cursor color toggle
:cursor_blink_loops
	DAT 0x00

;Color of cursor background
:cursor_color
	DAT 0x00

;Number of typed command chars
:command_length
	DAT 0x00

;26-char buffer + NULL
:command_buffer
	DAT 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00

;Current score value
:score
	DAT 0x00

;Current room
; 0 - Yon Dungeon
; 1 - Parapets
; 2 - Escarpment
; 3 - Dennis
:current_room
 	DAT 0x00

;Yon Dungeon State
; 0 - Start
; 1 - Took Ye Scroll
; 2 - Definitely No Ye Scroll
:yondungeon_state
 	DAT 0x00

;Escarpment State
; 0 - Start
; 1 - Took Ye Trinket
; 2 - Definitely No Ye Trinket
:escarpment_state
 	DAT 0x00

;Number of time the player has tried to get ye flask
:getyeflask_attempts
 	DAT 0x00

:vxtec_proc_scratch
 	DAT 0x00

;This scratch space is considerably more than 1 word, but
;but this is just here to mark it off and consumers should
;add to the pointer to use the rest of the space
:scratch_space
 	DAT 0x00
:scratch_space_1
 	DAT 0x00

