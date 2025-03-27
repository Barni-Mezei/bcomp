"""
Assembly version: bcomp assembly V1.1
LUA version: 5.3

Resources:
https://huggingface.co/learn/nlp-course/chapter6/8
https://www.lua.org/manual/5.3/manual.html


Made by: Barni - 2025.03.14

[x] Normalisation    - convert to utf8
[x] Pre-tokenisation - split by whitespaces / punctuation + determine string literals
[ ] Model            - Create actual token list
[ ] Postprocessor    - add additional tokens, correct missing tokens
"""

import sys
import os
import argparse
from enum import Enum
import pprint
import re
from lib.lib import *

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

# Parse command line arguments
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

TOKEN_SEPARATORS = ['\n', ' ', ',', ':', '.', '(', ')', '{', '}', '[', ']']
OPERATORS = ['=', '+', '-', '*', '/', '%', '^', '&', '|', '~', '<', '>',
             '<=', '>=', '==', '<<', '>>', '//', '~=', '#', '::', '..']
BLOCK_BOUNDARY = ['\n', 'end']
STRING_BOUNDARY = ['"', "'", '`']
KEYWORDS = ['and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 'function', 'goto', 'if', 'in',
            'local', 'nil', 'not', 'or', 'repeat', 'return', 'then', 'true', 'until', 'while']

class TokenType(Enum):
    UNKNOWN = -1
    KEYWORD = 0
    COMMENT = 1
    IDENTIFIER = 2
    TABLE = 3
    OPERATOR = 4
    STRING_LITERAL = 5
    NUMBER_LITERAL = 6
    BOOL_LITERAL = 7
    ELLIPSIS = 8
    NIL = 9
    EXPRESSION_START = 10 # (
    EXPRESSION_END = 11 # )
    SPECIAL = 99 # The control characters

class Token:
    type = TokenType.UNKNOWN
    value = ""

    def __init__(self, type : TokenType = TokenType.UNKNOWN, value : str = "") -> None:
        self.type = type
        self.value = value

    def fromString(self, string : str) -> None:
        self.type = getTokenType(string)
        self.value = string

    def __str__(self):
        text_color = WHITE

        match self.type:
            case TokenType.UNKNOWN: text_color = GRAY
            case TokenType.KEYWORD: text_color = RED
            case TokenType.COMMENT: text_color = GRAY
            case TokenType.IDENTIFIER: text_color = WHITE
            case TokenType.TABLE: text_color = WHITE
            case TokenType.OPERATOR: text_color = AQUA
            case TokenType.STRING_LITERAL: text_color = YELLOW
            case TokenType.NUMBER_LITERAL: text_color = AQUA
            case TokenType.BOOL_LITERAL: text_color = GREEN
            case TokenType.ELLIPSIS: text_color = AQUA
            case TokenType.NIL: text_color = RED
            case TokenType.EXPRESSION_START: text_color = WHITE
            case TokenType.EXPRESSION_END: text_color = WHITE
            case TokenType.SPECIAL: text_color = RED

        return f"{text_color}{str(self.type).split('.')[1]:<20}{WHITE}{RED + self.value.replace(chr(9), '') + WHITE if self.type == TokenType.SPECIAL else repr(self.value)}"

def print_tokens(token_list : list) -> None:
    if len(token_list) == 0: return
    if not isinstance(token_list[0], Token): return

    for token in token_list:
        print(token)

def raise_error(message : str = "- not specified -"):
    print(f"{RED}ERROR: {message}{WHITE}")
    exit()

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

    # Tokenise code (by the separators)
    for char in code_string:
        if escaped:
            current_token += char
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        # String ends
        if current_string_boundary != "" and (char == current_string_boundary or char == "\n"):
            current_string_boundary = ""
            current_token += char
            out.append({"token": current_token, "separator": " "})
            current_token = ""
            continue

        # String starts
        if current_string_boundary == "" and char in STRING_BOUNDARY:
            current_string_boundary = char
            current_token += char
            continue

        # Inside a string
        if current_string_boundary != "":
            current_token += char
            continue

        if char in TOKEN_SEPARATORS or char in OPERATORS:
            out.append({"token": current_token, "separator": char})
            current_token = ""
            continue

        current_token += char

    if len(current_token) > 0: out.append({"token": current_token, "separator": "\n"})

    # Remove unnecessary spaces + combine certain tokens into one
    had_new_line = False

    for token_data in out:
        # Exclude spaces
        if len(token_data["token"]) == 0 and token_data["separator"] == " ":
            continue

        # Add only 1 new line if multiple trailing ones found
        if len(token_data["token"]) == 0 and token_data["separator"] == "\n":
            if not had_new_line:
                had_new_line = True
                tmp.append(token_data)
            continue
        else:
            had_new_line = False

        tmp.append(token_data)

    out = []

    # Flatten out array
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

    tmp = out
    out = []

    # Multi token patterns, that needs to be combined
    patterns = ['--', '[[', ']]', '<<', '>>', '//', '==', '~=', '<=', '>=', '...']

    index = 0
    while index < len(tmp):
        token = tmp[index]
        index += 1

        # End of line separator
        if token == "\n":
            out.append("\tEOL")
            continue

        # Find and replace patterns
        pattern_found = False
        for pattern in patterns:
            result = False
            for offset, char in enumerate(pattern):
                if index-1 + offset < len(tmp) and tmp[index-1 + offset] == char:
                    result = True
                else:
                    result = False
                    break

            if result:
                out.append(pattern)
                index += len(pattern) - 1
                pattern_found = True
                break

        # Exit if a pattern is found
        if pattern_found: continue

        out.append(token)

    # End of file separator
    #out.append("\tEOL")
    out.append("\tEOF")

    tmp = out
    out = []

    # Combine floats into one token
    index = 0
    while index < len(tmp):
        token = tmp[index]
        index += 1

        out.append(token)

        # End of line separator
        if getTokenType(token) != TokenType.NUMBER_LITERAL:
            continue

        if index - 2 > 0 and index < len(tmp)-1:
            prev = tmp[index-2]
            curr = token
            next = tmp[index]

            if next == ".": continue

            prev_is_number = getTokenType(prev) == TokenType.NUMBER_LITERAL
            next_is_number = getTokenType(next) == TokenType.NUMBER_LITERAL

            if prev_is_number:
                if next_is_number:
                    #print("Number pcn:", f"{prev}{curr}{next}")
                    out.pop()
                    out.pop()
                    out.append(f"{prev}{curr}{next}")
                    index += 1
                else:
                    #print("Number pc-:", f"{prev}{curr}")
                    out.pop()
                    out.pop()
                    out.append(f"{prev}{curr}")
            else:
                if next_is_number:
                    #print("Number -cn:", f"{curr}{next}")
                    out.pop()
                    out.append(f"{curr}{next}")
                    index += 1
                elif curr != ".":
                    #print("Number -c-:", f"{curr}")
                    pass

    # print out constructed tokens, nicely
    for token in out:
        if token == "\tEOL":
            print(f"{AQUA}|{WHITE}")
            continue
        
        if token == "\tEOF":
            print(f"{RED}End of file{WHITE}")
            continue

        print(token, end=" ")

    return out

###############
## The model ##
###############

indent_level = -1

def is_keyword(token : Token, value : str = "") -> bool:
    print("Is keyword?", token)
    if value == "":
        return token.type == TokenType.KEYWORD and token.value in KEYWORDS
    else:
        return token.type == TokenType.KEYWORD and token.value == value

def is_expression(token : Token, value : str = "") -> bool:
    if value == "":
        if token.type == TokenType.NIL: return True
        if token.type == TokenType.BOOL_LITERAL: return True
        if token.type == TokenType.NUMBER_LITERAL: return True
        if token.type == TokenType.STRING_LITERAL: return True
        if token.type == TokenType.ELLIPSIS: return True
        # functiondef
        # prefixexp
        # ...
    else:
        return is_expression(token) and token.value == value



def grammar_exp(code_pre_tokens : list):
    if is_expression(code_pre_tokens[0]):
        return code_pre_tokens[0]
    else:
        raise_error(f"Grammar error! {code_pre_tokens}")

def grammar_get_explist(code_tokens : list):
    out = []

    if len(code_tokens) == 0: return []
    if code_tokens[0].type != TokenType.IDENTIFIER: return []

    expected_separator = False
    for token in code_tokens:
        print(token, expected_separator)
        if expected_separator:
            if token.type == TokenType.UNKNOWN and token.value == ",":
                expected_separator = False
            elif token.type == TokenType.OPERATOR and token.value == "=":
                break
            else:
                raise_error("Invalid separator detected! (in varlist)")
        else:
            if token.type == TokenType.IDENTIFIER:
                out.append(token)
                expected_separator = True
            else:
                raise_error("Invalid identifier detected! (in varlist)")
                break

    return out

def grammar_get_varlist(code_tokens : list):
    out = []

    if len(code_tokens) == 0: return []
    if code_tokens[0].type != TokenType.IDENTIFIER: return []

    expected_separator = False
    for token in code_tokens:
        print(token, expected_separator)
        if expected_separator:
            if token.type == TokenType.UNKNOWN and token.value == ",":
                expected_separator = False
            elif token.type == TokenType.OPERATOR and token.value == "=":
                break
            else:
                raise_error("Invalid separator detected! (in varlist)")
        else:
            if token.type == TokenType.IDENTIFIER:
                out.append(token)
                expected_separator = True
            else:
                raise_error("Invalid identifier detected! (in varlist)")
                break

    return out

def grammar_statement(code_tokens : list):
    varlist = grammar_get_varlist(code_tokens)
    explist = grammar_get_explist(code_tokens[len(varlist)+1:])
    print_tokens(explist)
    return []
    pass

def grammar_block(code_tokens : list):
    return grammar_statement(code_tokens)
    #grammar_ret_statement(code_tokens)

def grammar_chunk(code_tokens : list):
    return grammar_block(code_tokens)

def getTokenType(token : str) -> TokenType:
    if token == "\tEOL" or token == "\tEOF": return TokenType.SPECIAL
    if token == "nil" or token == "NIL": return TokenType.NIL
    if token == "true" or token == "false": return TokenType.BOOL_LITERAL
    if token == "...": return TokenType.ELLIPSIS
    if token in KEYWORDS: return TokenType.KEYWORD
    if token in OPERATORS: return TokenType.OPERATOR
    if re.search("^\".*\"|\'.*\'$", token): return TokenType.STRING_LITERAL
    if re.search("^(?:[0-9_]*[\\.eE]?[0-9_]*|0[xX][0-9a-fA-F]+|0[bB][01]+)$", token): return TokenType.NUMBER_LITERAL
    if re.search("^[a-zA-Z_]\w*$", token): return TokenType.IDENTIFIER
    if token in "({[": return TokenType.EXPRESSION_START
    if token in ")}]": return TokenType.EXPRESSION_END

    return TokenType.UNKNOWN

def model_o(code_pre_tokens : list) -> list:
    global indent_level

    indent_level += 1
    print(indent_level * "\t", "Model:", code_pre_tokens)

    if len(code_pre_tokens) == 1:
        return [{"type": getTokenType(code_pre_tokens[0]), "value": code_pre_tokens[0]}]

    out = []
    last_token_index = 0
    line = {}

    is_inside_operator = False

    for index, token in enumerate(code_pre_tokens):
        if not is_inside_operator:
            if token in OPERATORS:
                line = {}
                line["left"] = model(code_pre_tokens[last_token_index:index])
                line["type"] = TokenType.OPERATOR
                line["value"] = token
                last_token_index = index
                is_inside_operator = True
                continue

            last_token_index = index

        if token in BLOCK_BOUNDARY or index == len(code_pre_tokens)-1:
            print(indent_level * "\t", "End" if index == len(code_pre_tokens)-1 else "Boundary")
            if is_inside_operator:
                line["right"] = model(code_pre_tokens[last_token_index+1:index])

                is_inside_operator = False

                out.append(line)
            else:
                for t in code_pre_tokens[last_token_index:index]:
                    out.append({"type": getTokenType(t), "value": t})

    print(indent_level * "\t", last_token_index)

    if last_token_index == 0:
        for t in code_pre_tokens:
            out.append({"type": getTokenType(t), "value": t})

    print(indent_level * "\t", "Returned:", out)

    indent_level -= 1
    return out

def model(code_pre_tokens : list) -> list:
    out = []

    for index, token in enumerate(code_pre_tokens):
        new_token = Token()
        new_token.fromString(token)
        print(new_token)
        out.append(new_token)

    #pp = pprint.PrettyPrinter(width=41, compact=True)
    #pp.pprint(out)
    return grammar_chunk(out)

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
        print()
        tokens = model(pre_tokens)

except FileNotFoundError as e:
    print(f"{RED}File not found!{WHITE}")
    exit()

print()
print()

#pp = pprint.PrettyPrinter(width=41, compact=True)
#pp.pprint(tokens)

for token in tokens:
    print(token)

#for line in tokens:
#    for token in line:
#        print(token, end=" ")
#    print("\n")


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