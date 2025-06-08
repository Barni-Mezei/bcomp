;asm2.0

$port_pins 0
$port_console 2

;--------;
;- Main -;
;--------;

:loop

inp $port_pins
adr 0
sta

mva 1
out $port_pins

jsr :delay

mva 0
out $port_pins

jsr :delay

jmp :loop

;------------;
;- Functions-;
;------------;

; Loops until adr0
:delay

:delay_loop
lda
dec 1
mca
sta
jio :delay_end
jmp :delay_loop
:delay_end
rtn