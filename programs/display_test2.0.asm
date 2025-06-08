;asm2.0

;------------------;
; Create constants ;
;------------------;

$i 0
$row 1

$console 1
$display_control 3
$display_row 4

;-------------------;
; Initialise memory ;
;-------------------;

adr $i
stv 17
adr $row
stv 0b10000000_00000000

;--------------;
; Main program ;
;--------------;

:loop   ; Loop uses memory[0] as iteration counter
adr $i  ; Load iteration counter
lda
dec 1   ; Decrease iteration counter
mca
jio :loop_end
sta     ; Save iteration counter

jsr :loop_body

jmp :loop
:loop_end

;jsr :flush_display

hlt

;-----------;
; Functions ;
;-----------;

; Shifts the row in memory and displays it
:loop_body

; Set row index
adr $i
lda
dec 1
mca
out $display_control

mab
mvb 15
sub
mca
inc 97
mca
out $console

; Output row
adr $row
lda
out $display_row

; Shift row
shr
mca
sta

rtn

;:flush_display
;mva 0b11000000_00000000
;out $display_control
;rtn