;---------;
; Testing ;
;---------;

lda 5
ldb 2
jsr :is_smaller
out 0

lda 4
ldb 9
jsr :is_smaller
out 0

lda 6
ldb 6
jsr :is_smaller
out 0

lda 1111
out 0

lda 5
ldb 2
jsr :is_equal
out 0

lda 4
ldb 9
jsr :is_equal
out 0

lda 6
ldb 6
jsr :is_equal
out 0

lda 1111
out 0

lda 5
ldb 2
jsr :is_bigger
out 0

lda 4
ldb 9
jsr :is_bigger
out 0

lda 6
ldb 6
jsr :is_bigger
out 0

hlt

;-----------;
; Functions ;
;-----------;


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