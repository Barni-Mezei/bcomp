;asm  1.1

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

$port_console 0
$port_display_control 1
$port_display_row 2
$port_keyboard 0
$port_number 1

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

adr $i3
ldi 11  ; Iteration count (+1)
adr $player_x
inp $port_number
mac
str

;--------------;
; Main program ;
;--------------;

adr $player_x
mov

jsr :get_player_row

lda $dash
out $port_console

adr $player_row_buffer
mov
out $port_console

hlt

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