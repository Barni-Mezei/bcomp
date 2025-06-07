;asm 2.0
$display_control 2
$display_row 3

MVA 0b10010110_11101101
OUT $display_row

MVA 3
OUT $display_control

MVA 0b00000011_11010000
OUT $display_row