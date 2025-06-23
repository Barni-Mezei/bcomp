"""
Assembly version: bcomp assembly V1.1
LUA version: 5.3

Resources:
https://huggingface.co/learn/nlp-course/chapter6/8
https://www.lua.org/manual/5.3/manual.html


Made by: Barni - 2025.06.23

[x] Lexer     - Generate tokens from the input string
[ ] Parser    - Generate tree from the tokens
[ ] Compiler  - Generate asssembly code with macros based on the previously generated tree
[x] Assembler - Create machine code from the assembly code
"""

from misc import *
from lexer import Lexer
#import parser

lexer = Lexer()

lexer.tokenise_file("test.lua")

print("Lexer output:")
line_num = 0
was_token = False
indent_char = " "
sep_char = " "
while t := lexer.next():
    if t.value == "\tEOF": break

    if t.row == line_num:
        if was_token:
            print(f"{sep_char}{t.color}{t.value}", end = WHITE)
        else:
            print(f"{indent_char*t.col}{t.color}{t.value}", end = WHITE)
            was_token = True
    else:
        print("\n" * (t.row - line_num), end = WHITE)
        line_num = t.row
        was_token = False
        if was_token:
            print(f"{sep_char}{t.color}{t.value}", end = WHITE)
        else:
            print(f"{indent_char*t.col}{t.color}{t.value}", end = WHITE)
            was_token = True
print("\n-----------------")