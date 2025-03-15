"""
Assembly version: bcomp assembly V1.1

Resources:
https://huggingface.co/learn/nlp-course/chapter6/8
https://www.lua.org/manual/5.3/manual.html


Made by: Barni - 2025.03.14

[x] Normalisation    - convert to utf8
[x] Pre-tokenisation - split by whitespaces / punctuation + determine string literals
[ ] Model            - Create actual token list
[ ] Postprocessor    - add additional tokens, correct missing tokens
[ ] Pre-compiler     - Generate assembly code, with placeholders
[ ] Compiler         - complete assembly code

TODO:
- Group expressions, for later evaluation

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

###############
## Constants ##
###############

TOKEN_SEPARATORS = ['\n', ' ', ',', ':', '.', '+', '-', '*', '/', '%', '^', '&', '|', '~', '<', '>', '(', ')', '{', '}', '[', ']']
OPERATORS = ['+', '-', '*', '/', '%', '^', '&', '|', '~', '<', '>']
STRING_BOUNDARY = ['"', "'", '`']

class TokenType(Enum):
    UNKNOWN = -1
    KEYWORD = 0
    COMMENT = 1
    FUNCTION = 2
    EXPRESSION = 3
    STRING_LITERAL = 4
    NUMBER_LITERAL = 5

class Token:
    type = TokenType.UNKNOWN
    value = ""

    def __init__(self, type : TokenType, value : str) -> None:
        self.type = type
        self.value = value

    def __str__(self):
        return f"{AQUA}({self.type}) {WHITE}{repr(self.value)}"


################
## Normaliser ##
################

def normalise(code_string) -> str:
    return code_string

###################
## Pre-tokeniser ##
###################

def pre_tokenise(code_string : str) -> list:
    current_token = ""
    escaped = False

    out = []
    tmp = []

    current_string_boundary = ""

    #Tokenise code (by the separators)
    for char in code_string:
        if escaped:
            current_token += char
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        #String ends
        if current_string_boundary != "" and (char == current_string_boundary or char == "\n"):
            current_string_boundary = ""
            current_token += char
            out.append({"token": current_token, "separator": " "})
            current_token = ""
            continue

        #String starts
        if current_string_boundary == "" and char in STRING_BOUNDARY:
            current_string_boundary = char
            current_token += char
            continue

        #Inside a string
        if current_string_boundary != "":
            current_token += char
            continue

        if char in TOKEN_SEPARATORS:
            out.append({"token": current_token, "separator": char})
            current_token = ""
            continue

        current_token += char

    if len(current_token) > 0: out.append({"token": current_token, "separator": "\n"})

    #Remove unnecessary spaces + combine certain tokens into one
    had_new_line = False

    for token_data in out:
        #Exclude spaces
        if len(token_data["token"]) == 0 and token_data["separator"] == " ":
            continue

        #Add only 1 new line if multiple trailing ones found
        if len(token_data["token"]) == 0 and token_data["separator"] == "\n":
            if not had_new_line:
                had_new_line = True
                tmp.append(token_data)
            continue
        else:
            had_new_line = False

        tmp.append(token_data)

    out = []

    #Flatten out array
    for token_data in tmp:
        token = token_data["token"]
        separator = token_data["separator"]

        if len(token) == 0:
            out.append(separator)
        elif separator == " ":
            out.append(token)
        else:
            out.append(token)
            out.append(separator)

    return out

###############
## The model ##
###############

def model(code_pre_tokens : list) -> list:
    token_type = TokenType.UNKNOWN
    token = ""

    multiline_comment_flag = False

    out = []
    line = []

    for index, token in enumerate(code_pre_tokens):

        if token == "\n":
            if len(line) != 0: out.append(line)
            line = []
            continue

        line.append(token)

    if len(line) > 0: out.append(line)

    return out

########################################
## Tokenising (preparing compilation) ##
########################################

print(f"--- Tokenizing: {AQUA}{sys.argv[1]}{WHITE}")

tokens = []

try:
    with open(sys.argv[1], "r", encoding="utf8") as f:
        code_string = f.read()

        normalised_code = normalise(code_string)
        pre_tokens = pre_tokenise(normalised_code)
        tokens = model(pre_tokens)

except FileNotFoundError as e:
    print(f"{RED}File not found!{WHITE}")
    exit()

#for token in tokens:
#    print(f"{token["token"]}{AQUA}{repr(token["separator"])}{WHITE}")

for line in tokens:
    for token in line:
        print(token, end=" ")
    print("\n")


###############
## Compiling ##
###############

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