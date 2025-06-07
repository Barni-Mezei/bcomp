;asm1.1
lda 32
out 0

lda 33
out 0

:loop
ldb 1
add
mca
ldb 0b00000000_01111111
and

mca
jio :stop
out 0
jmp :loop

:stop
hlt