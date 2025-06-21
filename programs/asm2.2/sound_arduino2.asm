;asm  2.2

$port_pins 0
$port_console 1
$port_time 2

$beep_duration 2
$beep_start_time 3
$beep_delay 4

;------;
; Main ;
;------;

; 30 - 4 A   440Hz
; 20 - 5 A   880Hz
; 19 - 4 G#  415Hz
; 18 - 4 G#  415Hz

:loop

#forLoop 15 19 :sound 0
#forLoop 15 19 :sound 0
#forLoop 15 19 :sound 1
#forLoop 15 19 :sound 1

sta 20 ; Delay between pulses
stb 100 ; Note duration
jsr :beep

sta 0 ; Delay between pulses
stb 100 ; Note duration
jsr :beep

sta 20 ; Delay between pulses
stb 100 ; Note duration
jsr :beep

sta 0 ; Delay between pulses
stb 100 ; Note duration
jsr :beep

jmp :loop

hlt

:sound
;sta 18 ; Delay between pulses
stb 100 ; Note duration
jsr :beep
rtn

;sta 1
;out RA, $port_console


;-----------;
; Functions ;
;-----------;

; Delays RA milliseconds, runs in a loop
:beep
; Save delay
stw $beep_delay
svr RA

; Save duration
stw $beep_duration
svr RB

; Save starting time
inp RC, $port_time
;stw $start_time
;svr RC

:beep_loop
; Generate pulse (delay - on - delay - off)
str $beep_delay
lda RX

; Do not pulse if delay was 0
jio :beep_after_click

jsr :delay
stx 1
out RX, $port_pins

str $beep_delay
lda RX
jsr :delay
stx 0
out RX, $port_pins

:beep_after_click


; Get current time
inp RA, $port_time

; Get time difference (current - start)
mov RC, RB
sub RA

; Remove target duration (diff - duration)
str $beep_duration
lda RB
sub RA

; Loop if time diff < 0
jin :beep_loop

; Return if time diff was greater than duration
rtn



; Loops RX times
:delay
:delay_loop
dec RX, 1
jio :delay_end
jmp :delay_loop
:delay_end
rtn