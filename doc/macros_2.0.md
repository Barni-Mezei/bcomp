# Bcomp assembly 2.0 - macros

## loadStr
`#loadStr "<string>" <start address>`

### Arguments
- string: A chain of characters, in double quotes.
- start address: The memory address of the first character

### Description
This macro will load a string of text in to the memory, starting at the specified address, and putting each character after the previous one.

### Structure
The macro places 2 instructions after one a nother:

```
swv <address>
stv <char code>
```

### Example

```
;asm 2.0

#loadStr "Hello, world!\n" 0

```
```
Memory after the execution:
0: 72  (ascii code of 'H')
1: 101 (ascii code of 'e')
2: 108 (ascii code of 'l')
3: 108 (ascii code of 'l')
4: 111 (ascii code of 'o')
5: 444 (ascii code of ',')
. . .
```



## printStr
`#printStr <start address> <length> <counter address>`

### Arguments
- start address: The memory address of the first character
- length: The number of characters of the string
- counter address: A memory address, that can be used as a for loop's counter.

### Description
The macro will loop over each address in the memory, and prints it's content to **port2** (character output).

### Structure
The macro creates a simple loop, that iterates over the addresses, using the specified memory address as the loop counter.

```
swv <counter address>
stv 0
:loop
; load counter
adr <counter address>
lda
; Load character
sra
lda
out 2
; load counter again
srv <counter address>
lda
; increment counter
inc 1
mca
sta
enc <start index + length>
jio :end
jmp :loop
:end
```

### Example

```
;asm 2.0

#loadStr "Hello, world!\n" 0
#printStr 0 13 15
```



## forLoop
`#forLoop <start number> <end number> <label name> <counter address>`

### Arguments
- start number: Start of the iteration counter
- end number: End of the iteration counter
- label name: The name of a label, that will be called, in every iteration
- counter address: The memory address, that is used as a loop counter.

### Description
This macro wil create a loop, that runs `end number - start number` times, and jumps to the specified label. Each iteration, incerases the counter by 1 and before jumping to the label, the loop counter's value will be passed to the A register. The loop counter includes `start number` and `end number - 1`

### Structure
The macro creates a loop, very similar to the `#printStr`.

```
swv <counter address>
stv <start number>
:loop
; load counter
adr <counter address>
lda
; Jump to label
jsr <label name>
; load counter again
srv <counter address>
lda
; increment counter
inc 1
mca
sta
enc <end number>
jio :end
jmp :loop
:end
```

### Example

```
;asm 2.0

#forLoop 0 5 :fn 15

; Here, register A will hold numbers from 0 to 4
:fn
out 0
rtn
```



## reverseForLoop
`#reverseForLoop <start number> <end number> <label name> <counter address>`

### Arguments
- start number: Start of the iteration counter
- end number: End of the iteration counter
- label name: The name of a label, that will be called, in every iteration
- counter address: The memory address, that is used as a loop counter.

### Description
Same a s afor loop, but it counts down by 1 in each iteration. The loop counter includes `start number` and `end number + 1`

### Structure
Same as the `#forLoop` but with a `dec 1`

### Example

```
;asm 2.0

#reverseForLoop 5 0 :fn 15

; Here, register A will hold numbers from 5 to 1
:fn
out 0
rtn
```