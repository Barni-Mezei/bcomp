;asm 1.1

;------------------;
; Create constants ;
;------------------;

$i 0            ; Address of the iteration counter
$row_index 1    ; Address of the current row's index
$row 2          ; Address of the current row

;-------------------;
; Initialise memory ;
;-------------------;

adr $i
ldi 66  ; Iteration count (screens * 16 + 2)
adr $row_index
ldi 0  ; Row index for the display
adr $row
ldi 0b00001100_00000000  ; Current row of the display (start row)

;--------------;
; Main program ;
;--------------;

:loop   ; Loop uses memory[0] as iteration counter
adr $i  ; Load iteration counter
mov
ldb 1   ; Iteration decrease amount
sub     ; Decrease iteration counter
mca
jio :loop_end
str     ; Save iteration counter

; Loop content
jsr :loop_body

jmp :loop
:loop_end

;jsr :flush_display

hlt

;-----------;
; Functions ;
;-----------;

:flush_display
lda 0b11000000_00000000
out 1
rtn

; Shifts the row in memory and displays it
:loop_body
; Set display row index from memory[1]
adr $row_index
mov
out 1

; Increment row index
ldb 1
add
str

; Check if row index is at the -> flush the display
mac
ldb 1
sub
mca
ldb 0b00000000_00001111
and
mca
ldb 0b00000000_00001111
jsr :is_not_equal
jio :after_flush
jsr :flush_display
:after_flush

; Write row from memory to the screen
adr $row
mov
out 2

; Load row index (for calculating shift direction)
adr $row_index
mov
ldb 0b00000000_00001111
and
mca

; Check if is smaller than 4
ldb 8
jsr :is_smaller

; Load row data
adr $row
mov

jio :shift_right
; Not smaller (shift current row data ->)
shl
;mca
;shl
str
rtn

; Smaller
:shift_right    ; (shift current row data <-)
shr
;mca
;shr
str
rtn

;----------------;
; ** Math lib ** ;
;----------------;

;-----------;
; Less than ;
;-----------;
; Checks if RA is less than RB
; Returns: Check for the zero flag (true: smaller, false: bigger or equal)
:is_smaller
sub

jio :is_smaller_zero
jin :is_smaller_negative

lda 0   ; RA is larger
ldb 1
add     ; Zero flag: false
rtn

:is_smaller_zero
lda 0   ; Equals, not smaller
ldb 1
add     ; Zero flag: false
rtn

:is_smaller_negative
lda 1   ; RA is smaller
ldb 1
sub     ; Zero flag: true
rtn


;--------;
; Equals ;
;--------;
; Checks if RA is equal to RB
; Returns: Check for the zero flag (true: equal, false: smaller or bigger)
:is_equal
xor

jio :is_equal_zero

lda 0   ; Not equal
rtn

:is_equal_zero
lda 1   ; Equals
rtn


;------------;
; Not Equals ;
;------------;
; Checks if RA is not equal to RB
; Returns: Check for the zero flag (true: smaller or bigger, false: equal)
:is_not_equal
xor

jio :is_not_equal_zero

lda 1   ; Not equal
ldb 1
sub
rtn

:is_not_equal_zero
lda 0   ; Equals
ldb 1
add
rtn


;--------------;
; Greater than ;
;--------------;
; Checks if RA is greater than RB
; Returns: Check for the zero flag (true: greater, false: smaller or equals)
:is_bigger
sub

jio :is_bigger_zero
jin :is_bigger_negative

lda 1   ; RA is larger
ldb 1
sub     ; Zero flag: true
rtn

:is_bigger_zero
lda 0   ; Equals
ldb 1
add     ; Zero flag: false
rtn

:is_bigger_negative
lda 0   ; RA is smaller
ldb 1
add     ; Zero flag: false
rtn