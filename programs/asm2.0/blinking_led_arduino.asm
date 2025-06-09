;asm  2.0

$delay_amount 100

$port_pins 0
$port_console 1

;------;
; Main ;
;------;

:loop

mva 0b00000000_00000000
out $port_pins
mva 0
out $port_console

jsr :delay

mva 0b00000000_00000001
out $port_pins
mva 1
out $port_console

jsr :delay

mva 0b00000000_00000010
out $port_pins
mva 2
out $port_console

jsr :delay

jmp :loop


;-----------;
; Functions ;
;-----------;

:delay
adr 0
stv $delay_amount

:delay_loop
lda
dec 1
mca
sta
jio :delay_end
jmp :delay_loop

:delay_end
rtn