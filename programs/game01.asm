;asm1.1

;------------------;
; Create constants ;
;------------------;

$letter_a 97
$letter_b 98
$letter_c 99
$letter_d 100
$letter_e 101
$letter_f 102
$letter_g 103
$letter_h 104
$letter_i 105
$letter_j 106
$letter_k 107
$letter_l 108
$letter_m 109
$letter_n 110
$letter_o 111
$letter_p 112
$letter_q 113
$letter_r 114
$letter_s 115
$letter_t 116
$letter_u 117
$letter_v 118
$letter_w 119
$letter_x 120
$letter_y 121
$letter_z 122
$space 32
$line 95
$dash 45

$mask_up 0b10000000_00000000
$mask_left 0b01000000_00000000
$mask_down 0b00100000_00000000
$mask_right 0b00010000_00000000

; Output ports
$port_console 0
$port_display_control 1
$port_display_row 2

; Input ports
$port_keyboard 0
$port_number 1
$port_letter 2

$i 0            ; Address of the main iteration counter
$i2 1           ; Address of the display iteration counter
$i3 2           ; Address of the player row iteration counter
$row_index 5    ; Address of the row index counter
$player_row_buffer 6    ; The buffer of the currently generated player row
$player_x 10    ; Address of the player's x coordinate
$player_y 11    ; Address of the player's y coordinate

$level_start 100    ; The starting address of the level
$level_length 16    ; The length of the level

;-------------------;
; Initialise memory ;
;-------------------;

adr $i
ldi 11  ; Iteration count (+1)
adr $player_x
ldi 8
adr $player_y
ldi 8

; Load level
;adr 100
;ldi 0b11111111_11111111
;adr 101
;ldi 0b11000000_00000001
;adr 102
;ldi 0b10100000_00000001
;adr 103
;ldi 0b10010000_00000001
;adr 104
;ldi 0b10001000_00000001
;adr 105
;ldi 0b10000100_00000001
;adr 106
;ldi 0b10000010_00000001
;adr 107
;ldi 0b10000001_00000001
;adr 108
;ldi 0b10000000_10000001
;adr 109
;ldi 0b10000000_01000001
;adr 110
;ldi 0b10000000_00100001
;adr 111
;ldi 0b10000000_00010001
;adr 112
;ldi 0b10000000_00001001
;adr 113
;ldi 0b10000000_00000101
;adr 114
;ldi 0b10000000_00000011
;adr 115
;ldi 0b11111111_11111111

adr 100
ldi 0b11111111_11111111
adr 101
ldi 0b10000000_00000001
adr 102
ldi 0b10000000_00000001
adr 103
ldi 0b10000000_00000001
adr 104
ldi 0b10000000_00000001
adr 105
ldi 0b10000000_00000001
adr 106
ldi 0b10000000_00000001
adr 107
ldi 0b10000000_00000001
adr 108
ldi 0b10000000_00000001
adr 109
ldi 0b10000000_00000001
adr 110
ldi 0b10000000_00000001
adr 111
ldi 0b10000000_00000001
adr 112
ldi 0b10000000_00000001
adr 113
ldi 0b10000000_00000001
adr 114
ldi 0b10000000_00000001
adr 115
ldi 0b11111111_11111111

;--------------;
; Main program ;
;--------------;

:loop

jsr :loop_body
;nop

jmp :loop

;-------;
; Jumps ;
;-------;
:loop_body

; Read user input (and store it to memory[255])
adr 255
inp $port_keyboard
mac
str
;out $port_console

; Check if W is pressed
adr 255
mov
ldb $mask_up
and
mca
ldb 0
jsr :is_not_equal
jio :pressed_up
:after_press_up

; Check if A is pressed
adr 255
mov
ldb $mask_left
and
mca
ldb 0
jsr :is_not_equal
jio :pressed_left
:after_press_left

; Check if S is pressed
adr 255
mov
ldb $mask_down
and
mca
ldb 0
jsr :is_not_equal
jio :pressed_down
:after_press_down

; Check if D is pressed
adr 255
mov
ldb $mask_right
and
mca
ldb 0
jsr :is_not_equal
jio :pressed_right
:after_press_right

;lda $dash
;out $port_console

; Print player coordinates
;lda $letter_x
;out $port_console
;adr $player_x
;mov
;out $port_console
;
;lda $letter_y
;out $port_console
;adr $player_y
;mov
;out $port_console

; Render level
jsr :render_level

rtn



:pressed_up
;lda $letter_u
;out $port_console
adr $player_y   ; Player y -= 1
mov
ldb 1
sub
str
jmp :after_press_up


:pressed_left
;lda $letter_l
;out $port_console
adr $player_x   ; Player x -= 1
mov
ldb 1
sub
str
jmp :after_press_left


:pressed_down
;lda $letter_d
;out $port_console
adr $player_y   ; Player y += 1
mov
ldb 1
add
str
jmp :after_press_down


:pressed_right
;lda $letter_r
;out $port_console
adr $player_x   ; Player x += 1
mov
ldb 1
add
str
jmp :after_press_right


:render_level
; Reset display row index
adr $row_index
ldi 0

; Set iteration counter
adr $i2
lda $level_length    ; Iteration count (+1)
ldb 1
add
str

lda $dash
;out $port_console

:loop2   ; Loop uses memory[0] as iteration counter
adr $i2  ; Load iteration counter
mov
ldb 1   ; Iteration decrease amount
sub     ; Decrease iteration counter
mca
jio :loop2_end
str     ; Save iteration counter

; Loop content
jsr :loop2_body

jmp :loop2
:loop2_end

jsr :display_flush

rtn

; Display row iteration
:loop2_body
adr $row_index  ; Incement row index
mov
ldb 1
add
str

out $port_display_control   ; Send row index to display

; Empty row buffer
adr $player_row_buffer
ldi 0b00000000_00000000

; Check if this is the row with the player on it
mab
adr $player_y
mov
jsr :is_not_equal
jio :not_same_row

jsr :get_player_row
adr $player_row_buffer
mov
;out $port_console

:not_same_row

; Calculate addres from rowindex + offset
adr $row_index
mov
ldb $level_start
add
mca
ldb 1
sub
mca
;out $port_console


; Get row from memory
ara
mov
mab

; Get buffered row
adr $player_row_buffer
mov
bor
mca
out $port_display_row   ; Send row to display

rtn




;-----------;
; Functions ;
;-----------;

;----------------;
; Get player row ;
;----------------;
; Input: RA: player x
; Places a row with only 1 bit on, in to RAC
:get_player_row

adr $i3
ldi 16   ; 2 bytes (16) + 1

adr $player_row_buffer  ; Start shifting <- 1 bit from the left
ldi 0b00000000_00000001

:loop3   ; Loop uses memory as iteration counter
adr $i3  ; Load iteration counter
mov
ldb 1   ; Iteration decrease amount
sub     ; Decrease iteration counter
mca
jio :loop3_end
str     ; Save iteration counter

; Loop content
jsr :loop3_body

jmp :loop3
:loop3_end

rtn

; While constructiong the row
:loop3_body

; Shift row buffer <- by 1
adr $player_row_buffer
mov
shl
str
mca

; Check if it is the correct iteration number
adr $i3
mov
mab
adr $player_x
mov
jsr :is_equal
jio :stop_loop3
rtn

; Exit loop if iteration number = player_x
:stop_loop3
adr $player_row_buffer  ; Shift back -> by 1
mov
shr
str
adr $i3 ; Stop looping
ldi 1
rtn

;---------------;
; Flush display ;
;---------------;
:display_flush
lda 0b11000000_00000000
out $port_display_control
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