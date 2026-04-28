;asm 2.2

$port_neo_display 7

; Clear display
sta 0b111_0_11_0000_000000
out RA, $port_neo_display

; Load image drawing code
stw 0
svv 0b001_0_10_0000_000000
stw 1
svv 0b011_0_10_0000_000001
stw 2
svv 0b010_0_10_0000_000010
stw 3
svv 0b110_0_10_0000_000011
stw 4
svv 0b100_0_10_0000_000100
stw 5
svv 0b101_0_10_0000_000101
stw 6
svv 0b111_0_10_0000_000110

#forLoop 0 16 :y_loop 15

hlt

; Y loop
:y_loop
mov RA, RY

#forLoop 0 7 :draw_loop 14

rtn

; Rainbow drawing loop
:draw_loop
; Save loop counter
mov RA, RRADR

; Get shifted Y offset
mov RY, RA
msk 0b00000000_00001111
mov RC, RA
shl RA
shl RA
shl RA
shl RA
shl RA
shl RA
mov RA, RB

; Read display command from RAM
;mov RX, RRADR
lda RA

; Merge Y offset into the command
bor RA

; Execute command
out RA, $port_neo_display

rtn
