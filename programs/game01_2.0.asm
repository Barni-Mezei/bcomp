;asm2.0

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

$mask_left 0b00000000_00000001
$mask_right 0b00000000_00000010
$mask_up 0b00000000_00000100
$mask_down 0b00000000_00001000

; Output ports
$port_console 1
$port_display_control 3
$port_display_row 4

; Input ports
$port_keyboard 0
$port_number 1

$i 0            ; Address of the main iteration counter
$i2 1           ; Address of the display iteration counter
$i3 2           ; Address of the player row iteration counter
$row_index 3    ; Address of the row index counter
$player_row_buffer 4    ; The buffer of the currently generated player row
$player_x 5    ; Address of the player's x coordinate
$player_y 6    ; Address of the player's y coordinate

$level_start 8    ; The starting address of the level
$level_length 16    ; The length of the level

$user_input 7

;-------------------;
; Initialise memory ;
;-------------------;

adr $i
stv 11  ; Iteration count (+1)
adr $player_x
stv 8
adr $player_y
stv 8

; Load level

mva $level_start
swa
stv 0b11111111_11111111
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b10000000_00000001
inc 1
mca
swa
stv 0b11111111_11111111

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

; Read user input (and store it)
adr $user_input
inp $port_keyboard
sta
;out $port_console

; Check if W is pressed
adr $user_input
lda
mvb $mask_up
and
mca
mvb 0
jsr :is_not_equal
jio :pressed_up
:after_press_up

; Check if A is pressed
adr $user_input
lda
mvb $mask_left
and
mca
mvb 0
jsr :is_not_equal
jio :pressed_left
:after_press_left

; Check if S is pressed
adr $user_input
lda
mvb $mask_down
and
mca
mvb 0
jsr :is_not_equal
jio :pressed_down
:after_press_down

; Check if D is pressed
adr $user_input
lda
mvb $mask_right
and
mca
mvb 0
jsr :is_not_equal
jio :pressed_right
:after_press_right

;mva $dash
;out $port_console

; Print player coordinates
;mva $letter_x
;out $port_console
;adr $player_x
;lda
;out $port_console
;
;mva $letter_y
;out $port_console
;adr $player_y
;lda
;out $port_console

; Render level
jsr :render_level

rtn



:pressed_up
;mva $letter_u
;out $port_console
adr $player_y   ; Player y -= 1
lda
dec 1
mca
sta
jmp :after_press_up


:pressed_left
;mva $letter_l
;out $port_console
adr $player_x   ; Player x += 1
lda
inc 1
mca
sta
jmp :after_press_left


:pressed_down
;mva $letter_d
;out $port_console
adr $player_y   ; Player y += 1
lda
inc 1
mca
sta
jmp :after_press_down


:pressed_right
;mva $letter_r
;out $port_console
adr $player_x   ; Player x -= 1
lda
dec 1
mca
sta
jmp :after_press_right



:render_level
; Reset display row index
adr $row_index
stv 0

; Set iteration counter
adr $i2
mva $level_length    ; Iteration count (+1)
inc 1
mca
sta

;mva $dash
;out $port_console

:loop2   ; Loop uses memory[0] as iteration counter
adr $i2  ; Load iteration counter
lda
dec 1
mca
jio :loop2_end
sta     ; Save iteration counter
; Loop content
jsr :loop2_body
jmp :loop2

:loop2_end
jsr :display_flush

rtn

; Display row iteration
:loop2_body
adr $row_index  ; Incement row index
lda
inc 1
mca
sta

; Undo row index incrementation, for this output
dec 1
mca
out $port_display_control   ; Send row index to display


; Empty row buffer
adr $player_row_buffer
stv 0b00000000_00000000

; Check if this is the row with the player on it
mab
adr $player_y
lda
jsr :is_not_equal
jio :not_same_row

jsr :get_player_row
adr $player_row_buffer
lda
;out $port_console

:not_same_row

; Calculate addres from rowindex + offset
adr $row_index
lda
mvb $level_start
add
mca
mvb 1
sub
mca
;out $port_console


; Get row from memory
sra
lda
mab

; Get buffered row
adr $player_row_buffer
lda
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
stv 16   ; 2 bytes (16) + 1

adr $player_row_buffer  ; Start shifting <- 1 bit from the left
stv 0b00000000_00000001

:loop3   ; Loop uses memory as iteration counter
adr $i3  ; Load iteration counter
lda
dec 1
mca
jio :loop3_end
sta     ; Save iteration counter

; Loop content
jsr :loop3_body

jmp :loop3
:loop3_end

rtn



; While constructiong the row
:loop3_body

; Shift row buffer <- by 1
adr $player_row_buffer
lda
shl
mca
sta
mca

; Check if it is the correct iteration number
adr $i3
ldb
adr $player_x
lda
jsr :is_equal
jio :stop_loop3
rtn

; Exit loop if iteration number = player_x
:stop_loop3
adr $player_row_buffer  ; Shift back -> by 1
lda
shr
mca
sta
adr $i3 ; Stop looping
stv 1
rtn

;---------------;
; Flush display ;
;---------------;
:display_flush
mva 0b11000000_00000000
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

mva 0   ; Not equal
rtn

:is_equal_zero
mva 1   ; Equals
rtn

;------------;
; Not Equals ;
;------------;
; Checks if RA is not equal to RB
; Returns: Check for the zero flag (true: smaller or bigger, false: equal)
:is_not_equal
xor

jio :is_not_equal_zero

mva 1   ; Not equal
mvb 1
sub
rtn

:is_not_equal_zero
mva 0   ; Equals
mvb 1
add
rtn