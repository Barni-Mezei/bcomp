;asm  2.2

$port_pins 0
$port_console 1
$port_time 2

$duration 1
$start_time 2

;--------;
;- Main -;
;--------;

; Delay in MS

#forLoop 0 9 :loop 0
hlt

:loop

out RA, $port_console

sta 950 ; Works on Arduino UNO approx. 1 seconds. (1000ms was slower, due to display updates)
jsr :delay

rtn

;-----------;
; Functions ;
;-----------;

; Delays RA milliseconds
:delay
; Save duration
stw $duration
svr RA

; Save starting time
inp RB, $port_time

:delay_loop
; Get current time
inp RA, $port_time

; Get time difference (current - start)
sub RA

; Save start time
mov RB, RC

; Remove target duration (diff - duration)
str $duration
lda RB
sub RA

; Load start time
mov RC, RB

; Loop if result was negative
jin :delay_loop

; Return if time diff was greater than duration
rtn