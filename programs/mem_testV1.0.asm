;asm  1.0

LDA 2   ; Load 2 numbers
LDB	4
ADD     ; Add them (6)
ADR	0
STR     ; Store to mem[0]

LDA	7   ; Load 2 numbers
LDB	4
ADD     ; Add them (11)
ADR	1
STR     ; Store to mem[1]

ADR	0   ; Load the 2 numbers from memory
MOV
SWP     ; Move A to B

ADR	1
MOV	
ADD     ; Add them (17)

LAC
OUT 0   ; Output the result
HLT