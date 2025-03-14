"""
Assembly version: bcomp assembly V1.1

Resources:
https://huggingface.co/learn/nlp-course/chapter6/8
https://www.lua.org/manual/5.3/manual.html


Made by: Barni - 2025.03.14

[x] Normalisation    - convert to utf8
[ ] Pre-tokenisation - split by whitespaces / punctuation
[ ] Model            - Create actual token list
[ ] Postprocessor    - add additional tokens, correct missing tokens
[ ] Pre-compiler     - Generate assembly code, with placeholders
[ ] Compiler         - complete assembly code
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

TOKEN_SEPARATORS = ['\n', ' ', ',', '(', ')', '{', '}', '[', ']']
INCLUDED_SEPARATORS = ['(', ')', '{', '}', '[', ']']
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

################
## Normaliser ##
################

def pre_tokenise(code_string : str) -> list:
    current_token = ""
    escaped = False

    pre_tokenised = []
    out = []

    #Tokenise code
    for index, char in enumerate(code_string):
        if escaped:
            current_token += char
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char in TOKEN_SEPARATORS:
            pre_tokenised.append({"token": current_token, "separator": char})
            current_token = ""
            continue

        current_token += char


    #Remove unnecessary spaces
    current_string_boundary = ""
    current_string = ""
    had_new_line = False

    for index, token_data in enumerate(pre_tokenised):
        if len(token_data["token"]) > 0 and token_data["token"][-1] == current_string_boundary:
            current_string_boundary = ""
            current_string += token_data["token"][:-1:]
            out.append({"token": current_string, "separator": token_data["separator"]})
            continue

        if len(token_data["token"]) > 0 and current_string_boundary == "" and token_data["token"][0] in STRING_BOUNDARY:
            current_string_boundary = token_data["token"][0]
            current_string = token_data["token"][1::] + token_data["separator"]
            continue

        if current_string_boundary != "":
            current_string += token_data["token"] + token_data["separator"]
            continue

        #Exclude spaces
        if len(token_data["token"]) == 0 and token_data["separator"] == " ":
            continue

        #Add only 1 new line if multiple trailing ones found
        if len(token_data["token"]) == 0 and token_data["separator"] == "\n":
            if not had_new_line:
                had_new_line = True
                out.append(token_data)
            continue
        else:
            had_new_line = False


        out.append(token_data)

    return out

def tokenise(code_string : str) -> list:
    token_type = TokenType.UNKNOWN
    token = ""

    multiline_comment_flag = False
    was_separator = False
    escaped = False
    end_token = False

    out = []

    line = []

    for index, char in enumerate(code_string):
        print(multiline_comment_flag, token)

        was_separator = False
        next_char = ""
        if index < len(code_string) - 1: next_char = code_string[index + 1]
        prev_char = ""
        if index > 1: prev_char = code_string[index - 1]

        if escaped:
            token += char
            continue

        if char == "\\":
            escaped = True

        if token_type == TokenType.STRING_LITERAL:
            if char == '"':
                end_token = True
            else:
                token += char
                continue

        if token_type == TokenType.COMMENT:
            if multiline_comment_flag and char == ']':
                end_token = True

            token += char

            if token == "--[[":
                multiline_comment_flag = True
                print("Multiline comment")

            if char != "\n" or multiline_comment_flag: continue

        if char in TOKEN_SEPARATORS or char == "\n" or end_token:
            if len(token) > 0:
                token_obj = Token(token_type, token)
                line.append(token_obj)
            token = ""
            was_separator = True

            if end_token:
                token_type = TokenType.UNKNOWN
                multiline_comment_flag = False
            end_token = False

            if char == "\n":
                token_type = TokenType.UNKNOWN
                out.append(line)
                line = []

            continue

        if token_type == TokenType.UNKNOWN and char == '"':
            token_type = TokenType.STRING_LITERAL
            continue

        if token == "--":
            token_type = TokenType.COMMENT
            print("Comment")

        token += char

    return out


print(f"--- Tokenizing: {AQUA}{sys.argv[1]}{WHITE}")

tokens = []

try:
    with open(sys.argv[1], "r", encoding="utf8") as f:
        code_string = f.read()

        normalised_code = normalise(code_string)
        pre_tokens = pre_tokenise(normalised_code)
        tokens = pre_tokens

except FileNotFoundError as e:
    print(f"{RED}File not found!{WHITE}")
    exit()


for token in tokens:
    print(f"{token["token"]}{AQUA}{repr(token["separator"])}{WHITE}")

#for line in tokens:
#    for token in line:
#        print(token)
#    print()


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