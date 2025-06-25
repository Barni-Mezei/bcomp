;asm 2.0

$char_space " "
$char_left_par "("
$char_right_par ")"
$char_add "+"
$char_sub "-"

$port_console_number 1

; Address of the 2 numbers
$buf_a 6
$buf_b 7

;-------;
; Setup ;
;-------;

; Address of the expression, and the token index
$token_index 9
$expression_length 13


#loadStr "(4+5) + (6-5)" 10 ; length 13
swv $token_index
stv 10

;------;
; Main ;
;------;

; value stack: a
; operator stack: b

:parsing_loop

; Get the current token
adr $token_index
lda
mab

; Increase token index
inc 1
mca
sta

; Get back token index
mba
sra
lda

; Decide action
enc $char_space
jio :fn_space

enc $char_left_par
jio :op_left_par

enc $char_right_par
jio :op_right_par

enc $char_add
jio :op_operand
enc $char_sub
jio :op_operand

; Probably was a number
jmp :fn_number

:parsing_loop_end

#loadStr "end\n" 0
#printStr 0 4 5

; No operation -> stop
hlt

;-----------;
; Functions ;
;-----------;

; Char was a space
:fn_space
#loadStr "spc\n" 0
#printStr 0 4 5

jmp :parsing_loop



; The char was a number ? (48 - 57)
:fn_number
dec 48

jin :fn_num_negative
mca
psa
#loadStr "num\n" 0
#printStr 0 4 5

jmp :parsing_loop

:fn_num_negative
jmp :parsing_loop_end



; Char was "("
:op_left_par
#loadStr "lp(\n" 0
#printStr 0 4 5

pvb $char_left_par

jmp :parsing_loop



; Char was ")"
:op_right_par
#loadStr "rp)\n" 0
#printStr 0 4 5

:op_right_par_loop
; Pop operator stack
ppb
swv $buf_a
sta

; Discard left parenthesis and exit loop
enc $char_left_par
jio :parsing_loop

ppa ; get number a
swv $buf_b
sta
ppa ; get number b
mab

adr $buf_a
lda
stb

enc $char_add
jio :op_par_add
enc $char_sub
jio :op_par_sub

; Exit loop
jmp :parsing_loop


:op_par_add
#loadStr "add\n" 0
#printStr 0 4 5

srv $buf_a ; Get first number
lda
out $port_console_number
mab
srv $buf_b ; Get second number
lda
out $port_console_number
add ; Add
mca
out $port_console_number
psa ; Put back the result

jmp :op_right_par_loop


:op_par_sub
#loadStr "sub\n" 0
#printStr 0 4 5

srv $buf_a ; Get first number
lda
out $port_console_number
mab
srv $buf_b ; Get second number
lda
out $port_console_number
sub ; Subtract
mca
out $port_console_number
psa ; Put back the result

jmp :op_right_par_loop



; Char was "+" or "-"
:op_operand
#loadStr "op\n" 0
#printStr 0 4 5

; Store initial operand
swv $buf_a
sta

:op_operand_loop
; Pop operator stack
ppb

; Exit on empty stack
enc 0
jio :op_operand_loop_end

enc $char_add
jio :op_op_add
enc $char_sub
jio :op_op_sub

:op_operand_loop_end
; Put back the operator
srv $buf_a
lda
psb

; Exit loop
jmp :parsing_loop


:op_op_add
#loadStr "add\n" 0
#printStr 0 4 5

ppa ; Get first number
out $port_console_number
mab
ppa
out $port_console_number
add ; Add
mca
out $port_console_number
psa ; Put back the result

jmp :op_operand_loop


:op_op_sub
#loadStr "sub\n" 0
#printStr 0 4 5

ppa ; Get first number
out $port_console_number
mab
ppa
out $port_console_number
sub ; Subtract
mca
out $port_console_number
psa ; Put back the result

jmp :op_operand_loop