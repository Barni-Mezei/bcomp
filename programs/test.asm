;asm2.0

$port_pins 0
$port_console 2

$input 0

;--------;
;- Main -;
;--------;

:loop

inp $port_pins
adr $input
sta

jsr :shift
jsr :shift
jsr :shift
jsr :shift
jsr :shift
jsr :shift
jsr :shift
jsr :shift

mva 0
out $port_console
out $port_console

jmp :loop

;------------;
;- Functions-;
;------------;

:shift
lda
msk 1
mca

jio :zero

; one char
mva 49
out $port_console
jmp :end

:zero
; zero char
mva 48
out $port_console

:end

lda
shr
mca
sta

rtn