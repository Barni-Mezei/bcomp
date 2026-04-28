;asm 2.2

$port_neo_display 7

; Clear display
stw 0
svv 0b000_0_11_0000_000000

; Draw image
stw 1
svv 0b001_0_10_0000_000000
stw 2
svv 0b011_0_10_0000_000001
stw 3
svv 0b010_0_10_0000_000010
stw 4
svv 0b110_0_10_0000_000011
stw 5
svv 0b100_0_10_0000_000100
stw 6
svv 0b101_0_10_0000_000101
stw 7
svv 0b111_0_10_0000_000110

; Store loop max
; Set starting value
mov RWADR, RY
stx 0
out RX, $port_neo_display
out RY, $port_neo_display

:loop
inc RX, 1 ; Incremnt loop counter

; Read display command
mov RX, RRADR
lda RA
out RA, $port_neo_display

; Check if loop end was reached
mov RX, RA
mov RY, RB
sub RC

jio :loop_end
jmp :loop
:loop_end

hlt
