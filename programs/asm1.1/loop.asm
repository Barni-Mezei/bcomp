;asm  1.1

adr 0
ldi 10  ; Iteration count to memory[0] (needs to be 1 bigger than the desired amount)

:loop   ; Loop uses memory[0] as iteration counter
adr 0   ; Load iteration counter
mov
ldb 1   ; Iteration decrease amount
sub     ; Decrease iteration counter
mca
jio :loop_end
str     ; Save iteration counter

; Loop content
jsr :print_stuff

jmp :loop
:loop_end

hlt



;-----------;
; Functions ;
;-----------;

:print_stuff
lda 0
out 0
rtn