$apluszb1 1
$c_b1 2
$i 0
$port_console 0

$letter_m 109

LDA 111 ; az A értéke
LDB 260 ; a B értéke
ADD
ADR $apluszb1
STR

LDA 435
SUB
ADR $c_b1
STR


adr $apluszb1
mov
ldb 1
add
adr $i
str

adr $apluszb1
lda 0
mac
str

:loop   ; Loop uses memory[0] as iteration counter
adr $i   ; Load iteration counter
mov
ldb 1   ; Iteration decrease amount
sub     ; Decrease iteration counter
jio :loop_end
str     ; Save iteration counter

; Loop content
jsr :loopmultiply

jmp :loop
:loop_end

lda $letter_m
out $port_console
adr $apluszb1
mov
out $port_console


hlt



;-----------;
; Functions ;
;-----------;

:loopmultiply

adr $c_b1
mov
mab
adr $apluszb1
mov
add
str

;mca
out $port_console
rtn
