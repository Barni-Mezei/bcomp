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

def print_parse_tree(token : dict, indentation_level : int = 0) -> None:
    tab = " " * indentation_level
    tab2 = " " * (indentation_level + 4)

    #print("TOKEN", token)
    print(tab + f"{token['type'].replace("_", " ").capitalize()}:", end="")

    match token["type"]:
        case "var":
            print(f" '{token['value']}'")

        case "exp":
            if token['exp_type'] == "unary_expression":
                print(f" '{token['operand']}' (unop)")
                print_parse_tree(token['value'], indentation_level + 4)
            elif token['exp_type'] == "binary_expression":
                print(f" '{token['operand']}'")
                print_parse_tree(token['value_a'], indentation_level + 4)
                print_parse_tree(token['value_b'], indentation_level + 4)
            elif token['exp_type'] == "parenthesis":
                print(f" (")
                print_parse_tree(token['value'], indentation_level + 4)
                print(tab + ")")
            else:
                print(f" '{token['value']}' ({token['exp_type']})")

        case "varlist":
            print()
            for v in token["vars"]: print_parse_tree(v, indentation_level + 4)

        case "explist":
            print()
            for e in token["exps"]: print_parse_tree(e, indentation_level + 4)

        case "statement":
            print(f" ({token['stat_type']})")
            match token["stat_type"]:
                case "semicolon":
                    pass
                case "assignment":
                    print_parse_tree(token["varlist"], indentation_level + 4)
                    print_parse_tree(token["explist"], indentation_level + 4)
                case "keyword":
                    match token["value"]:
                        case "break":
                            print(tab2 + f"{RED}break{WHITE}")
                            pass
                        case "do":
                            print(tab2 + f"{RED}do{WHITE}")
                            print_parse_tree(token["block"], indentation_level + 4)
                            print(tab2 + f"{RED}end{WHITE}")
                            pass

        case "return_statement":
            print()
            print_parse_tree(token["explist"], indentation_level + 4)

        case "block":
            print()
            print(tab2 + f"Statements:")
            for s in token["statements"]: print_parse_tree(s, indentation_level + 8)

            if token["return_statement"]:
                print_parse_tree(token["return_statement"], indentation_level + 4)

try:
    parser = Parser(lexer.tokens) # Generates parse tree
except ParsingError as e:
    print(f"{RED}ERROR in file '{arguments.input_file}' on {e.place}:")
    print(f"{RED}\t{e}")
    exit()

print_parse_tree(parser.tree)

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