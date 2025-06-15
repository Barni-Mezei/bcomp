;asm  2.2

$port_pins 0
$port_console 1
$port_time 2

$beep_delay 5

;--------;
;- Main -;
;--------;

#forLoop 0 25 :play_sound 6
#reverseForLoop 25 1 :play_sound 7

hlt

:play_sound

out RA, 1
stb 300 ; Duration
jsr :beep

rtn


;-----------;
; Functions ;
;-----------;

; Loops until RB with RA delay
:beep
stw $beep_delay ; Delay
str $beep_delay
svr RA

:beep_main_loop

; Wait and turn on
lda RA
jsr :delay
stx 1
out RX, $port_pins

; Wait and turn off
lda RA
jsr :delay
stx 0
out RX, $port_pins

dec RB, 1
jio :beep_end
jmp :beep_main_loop
:beep_end

rtn

; Loops RA times
:delay
:delay_loop
dec RA, 1
;out RA, $port_console
jio :delay_end
jmp :delay_loop
:delay_end
rtn