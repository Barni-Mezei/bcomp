;asm  2.0

MVA 2   ; Load 2 numbers
MVB	4
ADD     ; Add them (6)
SWV	0
STA     ; Store to mem[0]

MVA	7   ; Load 2 numbers
MVB	4
ADD     ; Add them (11)
SWV	1
STA     ; Store to mem[1]
MAB     ; Move to B

SRV	0   ; Load the 2 numbers from memory
LDA
SRV	1
LDB	
ADD     ; Add them (17)

MCA
OUT 0   ; Output the result
HLT