  ; generated by esotope-bfc (DCPU branch)
  SET A, 0x4000
  SET [A+11], 3
  SET [A+4], 1
  SET [A+5], 3
  SET [A+6], 3
  SET [A+12], 0
  SET [A+13], 0
  SET [A+14], 0
:L0
  IFE [A+11], 0
    SET PC, L1
  JSR getc
  SET [A+12], B
  ADD [A+12], 1
  ADD [A+13], 4
  SET PUSH, 0
  SET B, [A+13]
  SHL B, 2
  ADD PEEK, B
  ADD [A+14], POP
  SET [A+13], 0
:L2
  IFE [A+14], 0
    SET PC, L3
:L4
  IFE [A+12], 0
    SET PC, L5
  SUB [A+12], 1
:L6
  IFE [A+12], 0
    SET PC, L7
  SUB [A+12], 1
  ADD A, 1
  SET PC, L6
:L7
  SET PC, L4
:L5
:L8
  IFE [A+13], 0
    SET PC, L9
  SUB A, 1
  SET PC, L8
:L9
  SUB [A+14], 1
  SET PC, L2
:L3
:L10
  IFE [A+12], 0
    SET PC, L11
  ADD [A+13], 1
  ADD [A+14], 1
  ADD [A+16], 1
  ADD [A+17], 1
:L12
  IFE [A+17], 0
    SET PC, L13
  SUB A, 4
  SET PC, L12
:L13
  ADD [A+16], 1
:L14
  IFE [A+18], 0
    SET PC, L15
  ADD [A+18], 1
  SUB A, 1
  SET PC, L14
:L15
:L16
  IFE [A+17], 0
    SET PC, L17
  ADD A, 1
  SET PC, L16
:L17
  ADD [A+18], 1
:L18
  IFE [A+18], 0
    SET PC, L19
:L20
  IFE [A+18], 0
    SET PC, L21
  ADD A, 3
  SET PC, L20
:L21
  ADD [A+20], 1
:L22
  IFE [A+20], 0
    SET PC, L23
  SUB A, 4
  SET PC, L22
:L23
  SUB [A+21], 1
  ADD A, 3
  SET PC, L18
:L19
  SUB [A+20], 1
  ADD [A+17], 1
  SET [A+18], 1
:L24
  IFE [A+20], 0
    SET PC, L25
  ADD [A+18], 1
:L26
  IFE [A+18], 0
    SET PC, L27
  ADD A, 1
  SET PC, L26
:L27
  ADD [A+20], 1
  SUB [A+15], 8
  ADD [A+16], 1
  ADD [A+17], 1
:L28
  IFE [A+15], 0
    SET PC, L29
  ADD [A+11], 1
  SUB [A+13], 1
:L30
  IFE [A+11], 0
    SET PC, L31
  ADD A, 1
  SET PC, L30
:L31
  SUB [A+8], 1
  SUB [A+10], 1
  ADD [A+12], 1
:L32
  IFE [A+8], 0
    SET PC, L33
  SUB [A+4], 1
  ADD [A+5], 1
:L34
  IFE [A+4], 0
    SET PC, L35
  ADD A, 2
  SET PC, L34
:L35
  SUB [A+2], 1
  SUB [A+3], 1
  SUB [A+65534], 4
  SUB [A+65535], 1
:L36
  IFE [A+65534], 0
    SET PC, L37
  SUB [A+65534], 1
  ADD [A+65535], 1
  SUB [A+65531], 1
:L38
  IFE [A+65534], 0
    SET PC, L39
  ADD [A+65531], 1
:L40
  IFE [A+65531], 0
    SET PC, L41
  ADD A, 1
  SET PC, L40
:L41
  SUB [A+65528], 1
  SUB [A+65529], 1
  ADD [A+65530], 1
  ADD [A+65532], 1
:L42
  IFE [A+65528], 0
    SET PC, L43
  ADD [A+65524], 1
  SUB [A+65525], 1
  ADD [A+65526], 1
:L44
  IFE [A+65524], 0
    SET PC, L45
  ADD A, 2
  SET PC, L44
:L45
  ADD [A+65523], 1
  SUB [A+65518], 1
  ADD [A+65519], 1
:L46
  IFE [A+65518], 0
    SET PC, L47
  SUB [A+65516], 1
:L48
  IFE [A+65516], 0
    SET PC, L49
  ADD A, 1
  SET PC, L48
:L49
  SUB [A+65518], 1
  SUB [A+65513], 1
  SUB [A+65514], 1
  SUB [A+65515], 1
:L50
  IFE [A+65513], 0
    SET PC, L51
  SUB [A+65509], 1
  ADD [A+65510], 1
:L52
  IFE [A+65509], 0
    SET PC, L53
  ADD A, 2
  SET PC, L52
:L53
  ADD [A+65505], 1
  ADD [A+65508], 1
  SUB [A+65503], 1
  ADD [A+65504], 1
:L54
  IFE [A+65503], 0
    SET PC, L55
  ADD [A+65499], 1
:L56
  IFE [A+65499], 0
    SET PC, L57
  ADD A, 1
  SET PC, L56
:L57
  SUB [A+65496], 1
  SUB [A+65498], 1
:L58
  IFE [A+65496], 0
    SET PC, L59
  ADD [A+65494], 1
:L60
  IFE [A+65494], 0
    SET PC, L61
  ADD A, 1
  SET PC, L60
:L61
  SUB [A+65496], 1
  SUB [A+65491], 1
  SUB [A+65492], 1
:L62
  IFE [A+65491], 0
    SET PC, L63
  SUB [A+65491], 1
  ADD [A+65492], 1
  SUB [A+65495], 1
  ADD [A+65496], 1
:L64
  IFE [A+65491], 0
    SET PC, L65
  SUB [A+65491], 1
  ADD [A+65493], 1
:L66
  IFE [A+65491], 0
    SET PC, L67
  SUB [A+65488], 1
  SUB [A+65489], 1
:L68
  IFE [A+65488], 0
    SET PC, L69
  ADD A, 1
  SET PC, L68
:L69
  SUB [A+65485], 1
  SUB [A+65486], 1
  SUB [A+65487], 1
  ADD [A+65489], 1
:L70
  IFE [A+65485], 0
    SET PC, L71
  ADD [A+65482], 1
  ADD [A+65483], 1
:L72
  IFE [A+65482], 0
    SET PC, L73
  ADD A, 1
  SET PC, L72
:L73
  SUB [A+65479], 1
  ADD [A+65480], 1
  ADD [A+65481], 1
:L74
  IFE [A+65479], 0
    SET PC, L75
  SUB [A+65479], 1
  SUB [A+65480], 1
  SUB [A+65481], 1
:L76
  IFE [A+65479], 0
    SET PC, L77
  SUB [A+65477], 1
:L78
  IFE [A+65477], 0
    SET PC, L79
  ADD A, 1
  SET PC, L78
:L79
  ADD [A+65475], 4
  ADD [A+65476], 1
  SET PUSH, 0
  SET B, [A+65475]
  SHL B, 3
  SUB PEEK, B
  ADD [A+65474], POP
  SET [A+65475], 2
:L80
  IFE [A+65474], 0
    SET PC, L81
  ADD [A+65472], 1
:L82
  IFE [A+65472], 0
    SET PC, L83
  ADD A, 1
  SET PC, L82
:L83
  SUB [A+65474], 1
  SUB [A+65469], 1
  SUB [A+65473], 1
:L84
  IFE [A+65469], 0
    SET PC, L85
  SUB [A+65469], 1
  SUB [A+65465], 1
  SUB [A+65467], 1
:L86
  IFE [A+65469], 0
    SET PC, L87
  ADD [A+65465], 1
:L88
  IFE [A+65465], 0
    SET PC, L89
  ADD A, 1
  SET PC, L88
:L89
  SUB [A+65462], 1
  ADD [A+65466], 1
:L90
  IFE [A+65462], 0
    SET PC, L91
  SUB [A+65458], 1
  ADD [A+65460], 1
:L92
  IFE [A+65458], 0
    SET PC, L93
  ADD A, 2
  SET PC, L92
:L93
  ADD [A+65457], 1
  SUB [A+65452], 1
  SUB [A+65453], [A+65452]
  SUB [A+65456], [A+65452]
  SET [A+65452], 0
  SUB A, 10
  SET PC, L90
:L91
  SUB A, 7
  SET PC, L86
:L87
  SET PC, L84
:L85
  SUB A, 5
  SET PC, L80
:L81
  SUB A, 5
  SET PC, L76
:L77
  SET PC, L74
:L75
  SUB A, 6
  SET PC, L70
:L71
  SUB A, 6
  SET PC, L66
:L67
  SET PC, L64
:L65
  SET PC, L62
:L63
  SUB A, 5
  SET PC, L58
:L59
  SUB A, 7
  SET PC, L54
:L55
  SUB A, 10
  SET PC, L50
:L51
  SUB A, 5
  SET PC, L46
:L47
  SUB A, 10
  SET PC, L42
:L43
  SUB A, 6
  SET PC, L38
:L39
  SET PC, L36
:L37
  SUB A, 10
  SET PC, L32
:L33
  SUB A, 7
  SET PC, L28
:L29
  SUB A, 5
  SET PC, L24
:L25
  ADD A, 8
  SET PC, L10
:L11
:L94
  IFE [A+13], 0
    SET PC, L95
:L96
  IFE [A+14], 0
    SET PC, L97
:L98
  IFE [A+14], 0
    SET PC, L99
:L100
  IFE [A+14], 0
    SET PC, L101
  SUB A, 4
  SET PC, L100
:L101
  ADD [A+15], 1
:L102
  IFE [A+17], 0
    SET PC, L103
  ADD A, 5
  SET PC, L102
:L103
  SUB [A+16], 1
  ADD A, 2
  SET PC, L98
:L99
  SUB A, 1
  SET PC, L96
:L97
  ADD [A+24], 1
  ADD [A+17], 1
  ADD A, 12
  SET PC, L94
:L95
  ADD A, 1
  SET PC, L0
:L1
  SET [A+10], 0
  ADD [A+1], 3
  ADD [A+2], 3
  ADD [A+3], 2
:L104
  IFE [A+1], 0
    SET PC, L105
:L106
  IFE [A+1], 0
    SET PC, L107
  ADD A, 1
  SET PC, L106
:L107
  ADD [A+7], 8
  SET PUSH, 1
  SET B, [A+7]
  MUL B, 6
  SUB PEEK, B
  SUB [A+6], POP
  SET PUSH, 0
  SET B, [A+7]
  SHL B, 2
  ADD PEEK, B
  ADD [A+5], POP
  SET [A+7], 0
:L108
  IFE [A+4], 0
    SET PC, L109
  SUB [A+4], 1
:L110
  IFE [A+4], 0
    SET PC, L111
  ADD [A+3], 1
  SET B, [A+5]
  JSR putc
  SUB [A+4], 1
  SET PC, L110
:L111
  SET PC, L108
:L109
:L112
  IFE [A], 0
    SET PC, L113
  SUB [A], 1
:L114
  IFE [A], 0
    SET PC, L115
  SUB [A], 1
  ADD [A+1], [A]
  SET [A], 0
  ADD A, 1
  SET PC, L114
:L115
:L116
  IFE [A+5], 0
    SET PC, L117
  SET B, [A+5]
  JSR putc
:L118
  IFE [A+5], 0
    SET PC, L119
  ADD A, 1
  SET PC, L118
:L119
  SET PC, L116
:L117
  ADD [A+2], [A+3]
  SET [A+3], 0
  SET PUSH, [A+6]
:L120
  IFE PEEK, 0
    SET PC, L121
  ADD [A+4], 2
  SET B, [A+4]
  AND B, 1
  IFE B, 0
    SET PC, L122
:L123
  SET PC, L123  ; infinite loop
:L122
  SET B, [A+4]
  SHR B, 1
  ADD [A+3], B
  SET [A+4], 0
  SUB PEEK, 1
  SET PC, L120
:L121
  SET O, POP
  SET [A+6], 0
  IFE [A+4], 0
    SET PC, L124
  SUB [A+4], 1
  ADD [A+5], 1
  SET PUSH, 0
  SET B, [A+4]
  SHL B, 1
  ADD PEEK, B
  ADD [A+3], POP
  SET [A+4], 0
:L124
  SET [A+4], 0
  ADD [A], [A+1]
  SET [A+1], 0
  SUB A, 3
  SET PC, L112
:L113
  ADD [A+2], 1
  SUB [A+5], 2
  SET PUSH, 0
  SET B, [A+5]
  MUL B, 0x5555
  SUB PEEK, B
  ADD [A+4], POP
  SET [A+5], 0
  SET B, [A+4]
  JSR putc
:L125
  IFE [A+6], 0
    SET PC, L126
  SET [A+6], 0
  SUB A, 2
  SET PC, L125
:L126
  ADD A, 4
  SET PC, L104
:L105
  SUB PC, 1
:screenoff
  DAT 0
:newline
  SET C, [screenoff]
  AND C, 0xffe0
  ADD C, 0x20
  SET [screenoff], C
  IFG 0x180, C
    SET PC, POP
:scroll
  SET C, 0
:scroll_loop
  SET [C+0x8000], [C+0x8020]
  ADD C, 1
  IFG 0x160, C
    SET PC, scroll_loop
:scroll_loop2
  SET [C+0x8000], 0
  ADD C, 1
  IFG 0x180, C
    SET PC, scroll_loop2
  SUB [screenoff], 0x20
  SET PC, POP
:putc
  IFE B, 10
    SET PC, newline
  IFG [screenoff], 0x17e
    JSR scroll
  SET C, [screenoff]
  BOR B, 0xf000
  SET [C+0x8000], B
  ADD C, 1
  SET [screenoff], C
  SET PC, POP
:getc
  IFG [inputsize], [inputoff]
    SET PC, getc_buffered
  SET B, 0
  SET C, [screenoff]
  XOR [C+0x8000], 0xff00
:getc_wait
  SET C, [keyoff]
:getc_busywait
  IFE [C], 0
    SET PC, getc_busywait
  ADD [keyoff], 1
  AND [keyoff], 0x900f
  SET O, [C]
  SET [C], 0
  IFE O, 10
    SET PC, getc_commit
  IFE O, 8
    SET PC, getc_bksp
  IFG O, 127
    SET PC, getc_wait
  IFG 32, O
    SET PC, getc_wait
  IFG B, 126
    SET PC, getc_wait
  SET [B+inputbuf], O
  SET C, [screenoff]
  BOR O, 0xf000
  SET [C+0x8000], O
  IFG C, 0x17e
    JSR scroll
  ADD [screenoff], 1
  SET C, [screenoff]
  XOR [C+0x8000], 0xff00
  ADD B, 1
  SET PC, getc_wait
:getc_bksp
  IFE B, 0
    SET PC, getc_wait
  SUB B, 1
  SET C, [screenoff]
  XOR [C+0x8000], 0xff00
  SET [C+0x7fff], 0x0f20
  SUB [screenoff], 1
  SET PC, getc_wait
:getc_commit
  SET C, [screenoff]
  XOR [C+0x8000], 0xff00
  JSR newline
  SET [B+inputbuf], 10
  ADD B, 1
  SET [inputsize], B
  SET [inputoff], 0
:getc_buffered
  SET C, inputoff
  SET B, [C]
  SET B, [B+inputbuf]
  ADD [C], 1
  SET PC, POP
:keyoff
  DAT 0x9000
:inputoff
  DAT 0
:inputsize
  DAT 0
:inputbuf
  DAT 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
:mem
  DAT 0  ; the start of memory
