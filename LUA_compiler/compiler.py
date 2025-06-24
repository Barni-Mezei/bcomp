"""
LUA version: 5.3

Resources:
https://www.lua.org/manual/5.3/manual.html


Made by: Barni - 2025.06.23

[x] Lexer     - Generate tokens from the input string
[ ] Parser    - Generate tree from the tokens
[ ] Compiler  - Generate asssembly code with macros based on the previously generated tree
[x] Assembler - Create machine code from the assembly code
"""

import importlib
import argparse
import os
from misc import *
from lexer import Lexer
from parser import Parser, ParsingError

arg_parser = argparse.ArgumentParser(
    exit_on_error = True,
    prog = "BCOMP LUA to Assmebly compiler",
    description = "This program compiles LUA scripts to BCOMP Assembly",
    usage="""Specify the file, containing the LUA code, set the output file name and the assembly version, and run the script.
IMPORTANT: Supported lua version: 5.3""",
)

arg_parser.add_argument('input_file', help="The path to your LUA source file")
arg_parser.add_argument('-o', '--output-path', help="The path of the output file, optionally containing the file name itself")
arg_parser.add_argument('-v', '--version', default="2.2", type=str, help="The assembly version. This must be specified!")

#Parse command line arguments
try:
    arguments = arg_parser.parse_args()
except Exception as e:
    print(f"{RED}ERROR: {str(e).capitalize()}{WHITE}")
    exit()


ASM_VERSION = arguments.version

print(f"--- Importing compiler: {AQUA}{ASM_VERSION}{WHITE}")

# Import the correct compiler version
COMPILER = None

try:
    COMPILER = importlib.import_module(f"compiler_asm{ASM_VERSION.replace('.', '_')}")
except Exception as e:
    print(f"{RED}ERROR: {str(e).capitalize()}{WHITE}")
    exit()

###################
# Generate tokens #
###################
print(f"--- Lexing source code")

# Start input file processing
lexer = Lexer()

# Try lexing the file
try:
    lexer.tokenise_file(arguments.input_file)
except Exception as e:
    print(f"{RED}ERROR: {str(e).capitalize()}{WHITE}")
    exit()

print("Lexer output:")
line_num = 0
was_token = False
indent_char = " "
sep_char = " "
for t in lexer.tokens:
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


################
# Parse tokens #
################
print(f"--- Parsing tokens")

try:
    parser = Parser(lexer.tokens) # Generates parse tree
except ParsingError as e:
    print(f"{RED}ERROR in file '{arguments.input_file}' on {e.place}:")
    print(f"{RED}\t{e}")
    exit()

# Get file path
def path_leaf(path):
    head, tail = os.path.split(path)
    return tail or os.basename(head)

def give_new_type(full_file_path, new_type):
    return ".".join(path_leaf(full_file_path).split(".")[0:-1]) + new_type

save_path = "../programs/" if os.path.exists("../programs/") else "./"
save_path += give_new_type(arguments.input_file, ".asm")

if arguments.output_path: save_path = arguments.output_path

###################
# Compile to file #
###################
print(f"--- Compiling to: {AQUA}{os.path.join(save_path)}{WHITE}")

compiler = COMPILER.Compiler(parser.tree) 

compiler.compile_to_file(save_path)