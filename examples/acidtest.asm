; Code Obfuscator
; https://gist.github.com/2327355


; The loader has nice properties shorter versions don't:
; 1. doesn't touch registers or stack
; 2. can be based anywhere via 'set a,stub'
; 3. exercises interpreters ;)
:stub xor [begin],0x5eed
                mul [2+a],25173 ; Grogono LCG
                add [2+a],13849
                sub [1+a],1
                ifg end,[1+a]
                set pc,a
; The obfuscated code should toggle a between 0 and 0xFFFF, forever.
; (Unless the assembler or interpreter are buggy.)
:begin dat 0xdaee
                dat 0xf121
                dat 0x5124
                dat 0xe2a2
:end
