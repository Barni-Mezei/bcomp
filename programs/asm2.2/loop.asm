;asm 2.2

$port_console 1

; Starting value
sta 7

:loop
dec 1, RA ; RA += 1
out RA, $port_console

jio :loop_end
jmp :loop
:loop_end

hlt