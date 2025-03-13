;------------------;
; Create constants ;
;------------------;

$port_console 0
$port_display_commands 1
$port_display 2

$row 0
$row_index 1

;-------------------;
; Initialise memory ;
;-------------------;

adr $row
ldi 0b00000000_00000001
adr $row_index
ldi 0

;--------------;
; Main program ;
;--------------;

; Draw line (16)
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra
jsr :balra

; Display current row
adr $row
mov
out $port_display

; Flush display
lda 0b11000000_00000000
out $port_display_commands

adr $row
ldi 0b01000000_00000000
adr $row_index
ldi 0

lda 0
out $port_display_commands

jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra
jsr :jobbra

; Flush display
lda 0b11000000_00000000
out $port_display_commands

hlt

;-----------;
; Functions ;
;-----------;

:balra
; Display current row
adr $row
mov
out $port_display

; Shift data
shl
adr $row
str

jsr :row++

rtn


:jobbra
; Display current row
adr $row
mov
out $port_display

; Shift data
shr
adr $row
str

jsr :row++

rtn



:row++

; Incerement row number
ldb 1
adr $row_index
mov
add
str

; Set display row index
mca
out $port_display_commands

rtn