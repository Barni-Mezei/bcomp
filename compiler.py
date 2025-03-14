"""
Assembly version: bcomp assembly V1.1
"""

import sys
import os
import argparse
from enum import Enum
from lib import *

arg_parser = argparse.ArgumentParser(
    exit_on_error = True,
    prog = "BCOMP assembly compiler",
    description = "This program compiles your '.lua' files in to '.asm' files",
    usage="To compile your code, you have to specify the path to the '.lua' file, and run it.\n"
    "If you want to specify the output location of the '.asm' file, you can use the -o parameter.\nIf you want to name your output file, you can use the -f parameter.\n"
    "For other additional information, please read the 'lua_compiler.md' file.",
)

arg_parser.add_argument('input_file', help="The path to your '.lua' file")
arg_parser.add_argument('-o', '--output-path', help="The path to the directory, that will contain your compiled code")
arg_parser.add_argument('-f', '--file-name', help="The name of your compiled file. Filetype will be ignored!")
arg_parser.add_argument('-w', '--warn', help="Disables all warning messages")
arg_parser.add_argument('-Wall', '--warn-all', help="Enables the extended warnining messages")

#Parse command line arguments
if len(sys.argv[1::]) == 0:
    print(f"{RED}No input file given!{WHITE}")
    exit()

if len(sys.argv) > 1 and not ".lua" in sys.argv[1]:
    print(f"{RED}Missing or invalid file type! (Must be .lua){WHITE}")
    exit()

try:
    arguments = arg_parser.parse_args()
except Exception as e:
    print(f"{RED}ERROR: {str(e).capitalize()}{WHITE}")
    exit()

########################
## Tokeniser function ##
########################

TOKEN_SEPARATOR = " "

class TokenType(Enum):
    UNKNOWN = -1
    KEYWORD = 0
    COMMENT = 1
    FUNCTION = 2
    EXPRESSION = 3
    LITERAL = 4

class Token:
    type = TokenType.UNKNOWN
    value = ""

    def __init__(self, type : TokenType, value : str) -> None:
        self.type = type
        self.value = value

def tokenise(code_string : str) -> list:
    token_type = ""
    token = ""
    can_read = True
    out = []

    for index, char in enumerate(code_string):
        if char == TOKEN_SEPARATOR:
            out.append(token)
            token = ""
            continue

        token += char

    return out


print(f"--- Tokenizing: {AQUA}{sys.argv[1]}{WHITE}")
try:
    with open(sys.argv[1], "r", encoding="utf8") as f:
        code_string = f.read()

        tokenise(code_string)

except FileNotFoundError as e:
    print(f"{RED}File not found!{WHITE}")
    exit()

print(f"--- Compiling: {AQUA}{sys.argv[1]}{WHITE}")


#Writing to file
def path_leaf(path):
    head, tail = os.path.split(path)
    return tail or os.basename(head)

def give_new_type(full_file_path, new_type):
    return ".".join(path_leaf(full_file_path).split(".")[0:-1]) + new_type

save_path = "./programs/" if os.path.exists("./programs/") else "./"
save_name = give_new_type(sys.argv[1], ".asm")

if arguments.output_path: save_path = arguments.output_path
if arguments.file_name: save_name = give_new_type(arguments.file_name + ".D", ".asm")

#f = open(save_path + save_name, "w", encoding="utf8")

print(f"--- Writing to: {AQUA}{os.path.join(save_path, save_name)}{WHITE}")
#for i,ins in enumerate(out[::2]):
    #print(f"{AQUA}{ins}\t{WHITE}{out[i*2+1]}\t({AQUA}{command_lookup[int(ins)]}{WHITE})")
#    f.write(f"{ins},{out[i*2+1]}{';' if i*2+2 < len(out) else ''}")

#f.close()