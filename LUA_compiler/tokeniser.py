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

"""
TODO:
- prefixexp -> functioncall
- prefixexp -> "(" <exp> ")"

BUG:
- exp -> Numeral -> ".5.4.3." evals to "3.0", so closng "." is stronger. -> basically no invalid numbers.
- exp -> Numeral -> "5." evals with the wrong place. (col and row)
- var -> prefixexp . Name -> "a.b." evals to "a.b.", so variable names and access paths must be validated again.

NOTE:
###############################
# The currently supported BNF #
###############################

chunk ::= block

block ::= stat

stat ::=
    ';' | 
    varlist '=' explist |

varlist ::= var {',' var}
var ::= Name | prefixexp . Name

explist ::= exp {',' exp}
exp ::=  nil | false | true | Numeral | LiteralString | '...' | prefixexp

prefixexp ::= var
"""

import sys
import os
import argparse
from enum import Enum
import pprint
import re
import random
from lib.lib import *
from lib.logTree import *

if __name__ == "__main__":
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

code_pointer = 0
max_recursion_depth = 32

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

class Character:
    row = 0
    col = 0

    def __init__(self, row : int, column : int) -> None:
        self.row = row
        self.col = column

class Token:
    type = TokenType.UNKNOWN
    value = ""
    _place : Character

    def __init__(self, type : TokenType = TokenType.UNKNOWN, value : str = "", row = -1, col = -1) -> None:
        self.type = type
        self.value = value
        self._place = Character(row, col)

    def fromString(self, string : str) -> None:
        self.type = getTokenType(string)
        self.value = string

    @property
    def place(self):
        return f"[Ln {str(self._place.row + 1)} Col {str(self._place.col + 1)}]"

    @property
    def row(self):
        return self._place.row

    @property
    def col(self):
        return self._place.col

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

        return f"{text_color}{str(self.type).split('.')[1]:<20}{WHITE}{self.place:<15}{(GREEN if self.value == '\tSOF' else RED) + self.value.replace(chr(9), '') + WHITE if self.type == TokenType.SPECIAL else repr(self.value)}"

def print_tokens(token_list : list, title : str = "") -> None:
    if len(token_list) == 0: return
    if not isinstance(token_list[0], Token): return

    if title != "":
        print(f"\n{title}")

    for token in token_list:
        print(token)

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
    line_number = 0
    column = 0

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
            out.append({"token": current_token, "separator": " ", "row": line_number, "col": column})
            column += len(current_token) + 1

            current_token = ""

            if char == "\n":
                line_number += 1
                column = 0

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
            out.append({"token": current_token, "separator": char, "row": line_number, "col": column})
            column += len(current_token) + 1

            current_token = ""

            if char == "\n":
                line_number += 1
                column = 0

            continue

        current_token += char

    if len(current_token) > 0:
        out.append({"token": current_token, "separator": "\n", "row": line_number, "col": column})

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
        separator_col = token_data["col"] + len(token)

        if len(token) == 0:
            out.append({"value": separator, "row": token_data["row"], "col": separator_col})
        elif separator == " ":
            out.append({"value": token, "row": token_data["row"], "col": token_data["col"]})
        else:
            out.append({"value": token, "row": token_data["row"], "col": token_data["col"]})
            out.append({"value": separator, "row": token_data["row"], "col": separator_col})

    tmp = out
    out = []

    # Multi token patterns, that needs to be combined
    patterns = ['--', '[[', ']]', '<<', '>>', '//', '==', '~=', '<=', '>=', '...', '..']

    index = 0
    while index < len(tmp):
        token = tmp[index]
        index += 1

        # Keep track of where are you in the file
        line_number = token["row"]
        column = token["col"] + len(token["value"])

        # End of line separator
        if token["value"] == "\n":
            #out.append("\tEOL")
            continue

        # Find and replace patterns
        pattern_found = False
        for pattern in patterns:
            result = False
            for offset, char in enumerate(pattern):
                if index-1 + offset < len(tmp) and tmp[index-1 + offset]["value"] == char:
                    result = True
                else:
                    result = False
                    break

            if result:
                out.append({"value": pattern, "row": token["row"], "col": token["col"]})
                index += len(pattern) - 1
                pattern_found = True
                break

        # Exit if a pattern is found
        if pattern_found: continue

        out.append(token)

    # Start of file separator (temporary, for float construction)
    out.insert(0, {"value":"\tSOF", "row": 0, "col": 0})

    # End of file separator
    out.append({"value":"\tEOF", "row": line_number, "col": column})

    # Combine floats into one token
    index = 0
    while index < len(out):
        token = out[index]
        token_value = token["value"]
        index += 1

        # Skip non-numeral tokens
        if token_value != "." and getTokenType(token_value) != TokenType.NUMBER_LITERAL:
            continue

        #WARNING: Th this point 'index' is already pointing to the next token!
        if index - 2 >= 0 and index <= len(out):
            prev = out[index - 2]
            prev_value = prev["value"]
            next = out[index]
            next_value = next["value"]

            if next_value == ".": continue

            prev_is_number = getTokenType(prev_value) == TokenType.NUMBER_LITERAL and not "." in prev_value
            next_is_number = getTokenType(next_value) == TokenType.NUMBER_LITERAL and not "." in next_value

            # print("Corrected INDEX:", index - 1, "Tokens:", out, "prev token:", prev,
            #       "current token:", token, "next token:", next,
            #       "prev is number?", prev_is_number, "next is number?", next_is_number,
            # sep = "\n")

            if prev_is_number:
                if next_is_number:
                    #print("Number pcn:", f"{prev_value}{token_value}{next_value}")
                    out.pop(index - 2)
                    out.pop(index - 2)
                    out.pop(index - 2)
                    out.insert(index - 2, {"value": prev_value+token_value+next_value, "row": prev["row"], "col": prev["col"]})
                    index += 1
                else:
                    #print("Number pc-:", f"{prev_value}{token_value}")
                    out.pop(index - 2)
                    out.pop(index - 2)
                    out.insert(index - 2, {"value": prev_value+token_value, "row": prev["row"], "col": prev["col"]})
            else:
                if next_is_number:
                    #print("Number -cn:", f"{token_value}{next_value}")
                    out.pop(index - 1)
                    out.pop(index - 1)
                    out.insert(index - 1, {"value": token_value+next_value, "row": token["row"], "col": token["col"]})
                elif token_value != ".":
                    #print("Number -c-:", f"{token_value}")
                    pass

    # Remove start of file separator (temporary for floats)
    out.pop(0)


    # print out constructed tokens, nicely
    """for token in out:
        if token["value"] == "\tEOL":
            print(f"{AQUA}|{WHITE}")
            continue
        
        if token["value"] == "\tEOF":
            print(f"{RED}End of file{WHITE}")
            continue

        if token["value"] == "\tSOF":
            print(f"{GREEN}Start of file{WHITE}", end=" ")
            continue

        print(token["value"], end=" ")"""

    return out

def tokenise(code_pre_tokens : list) -> list:
    out = []

    for index, token in enumerate(code_pre_tokens):
        new_token = Token(value = token["value"], type = getTokenType(token["value"]), row = token["row"], col = token["col"])
        out.append(new_token)

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

def getTokenType(token : str) -> TokenType:
    if token in ["\tEOL", "\tEOF", "\tSOF"]: return TokenType.SPECIAL
    if token == "nil" or token == "NIL": return TokenType.NIL
    if token == "true" or token == "false": return TokenType.BOOL_LITERAL
    if token == "...": return TokenType.ELLIPSIS
    if token in KEYWORDS: return TokenType.KEYWORD
    if token in OPERATORS: return TokenType.OPERATOR
    if re.search("^\".*\"|\'.*\'$", token): return TokenType.STRING_LITERAL
    if re.search("^(?:(?:(?:[0-9_]+\\.)|(?:\\.[0-9_]+)|(?:[0-9_]+\\.[0-9_]+)|(?:[0-9_]+)|(?:[0-9_]+[eE][0-9_]+))|0[xX][0-9a-fA-F]+|0[bB][01]+)$", token): return TokenType.NUMBER_LITERAL
    if re.search("^[a-zA-Z_]\\w*$", token): return TokenType.IDENTIFIER
    if token in "({[": return TokenType.EXPRESSION_START
    if token in ")}]": return TokenType.EXPRESSION_END

    return TokenType.UNKNOWN


###################
# Get <prefixexp> #
###################

def try_prefixexp_var(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if caller == "var" and recursion_depth >= max_recursion_depth: return False

    result = grammar_get_var(code_tokens, code_pointer, "prefixexp", recursion_depth)

    if result == False: return False
    return result[0], result[1]

def try_prefixexp_exp(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if caller == "exp" and recursion_depth >= max_recursion_depth: return False

    if code_tokens[code_pointer].value == "(":
        result = grammar_get_exp(code_tokens, code_pointer, "prefixexp", recursion_depth)

    return False

def try_prefixexp(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    # Try all defined prefixexps
    all_expressions = [
        try_prefixexp_var,  #Looks like: <var>
        #try_prefixexp_exp, #Looks like: "(" <exp> ")"
    ]

    # Return with the result
    for index, expression in enumerate(all_expressions):
        result = expression(code_tokens, code_pointer, caller, recursion_depth)
        if result != False: return result

    # Default to failure (no prefixexp found)
    return False

def grammar_get_prefixexp(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    #print(caller, "-> grammar_get_prefixexp", recursion_depth)
    if code_pointer < len(code_tokens) and code_tokens[code_pointer].value == "\tEOF": return False

    result = try_prefixexp(code_tokens, code_pointer, caller, recursion_depth + 1)

    if result == False: return False
    return result[0], result[1]


#############
# Get <exp> #
#############

# End of chain
def try_exp_nil(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].value == "nil":
        return {"type": "exp", "exp_type": TokenType.NIL, "value": "nil", "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

# End of chain
def try_exp_false(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].value == "false":
        return {"type": "exp", "exp_type": TokenType.BOOL_LITERAL, "value": "false", "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

# End of chain
def try_exp_true(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].value == "true":
        return {"type": "exp", "exp_type": TokenType.BOOL_LITERAL, "value": "true", "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

# End of chain
def try_exp_number(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].type == TokenType.NUMBER_LITERAL:
        return {"type": "exp", "exp_type": TokenType.NUMBER_LITERAL, "value": code_tokens[code_pointer].value, "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

# End of chain
def try_exp_string(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].type == TokenType.STRING_LITERAL:
        return {"type": "exp", "exp_type": TokenType.STRING_LITERAL, "value": code_tokens[code_pointer].value, "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

# End of chain
def try_exp_ellipsis(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].value == "...":
        return {"type": "exp", "exp_type": TokenType.ELLIPSIS, "value": "...", "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

def try_exp_prefixexp(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if caller == "prefixexp" and recursion_depth >= max_recursion_depth: return False

    result = grammar_get_prefixexp(code_tokens, code_pointer, "exp", recursion_depth)

    if result == False: return False
    return result[0], result[1]

def try_exp(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    # Try all defined statements
    all_expressions = [
        try_exp_nil,        # Looks like: "nil"
        try_exp_false,      # Looks like: "false"
        try_exp_true,       # Looks like: "true"
        try_exp_number,     # Looks like: "5" | "3.25"
        try_exp_string,     # Looks like: '"asd"' (between quotes)
        try_exp_ellipsis,   # Looks like: "..."
        try_exp_prefixexp,  # Looks like: <var> | "(" <exp> ")"
    ]

    # Return with the result
    for index, expression in enumerate(all_expressions):
        result = expression(code_tokens, code_pointer, caller, recursion_depth)
        #print("result", result)
        if result != False: return result

    # Default to failure (no expression found)
    return False

def grammar_get_exp(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    #print(caller, "-> grammar_get_exp", recursion_depth)
    if code_pointer < len(code_tokens) and code_tokens[code_pointer].value == "\tEOF": return False

    result = try_exp(code_tokens, code_pointer, caller, recursion_depth + 1)

    if result == False: return False
    return result[0], result[1]


#############
# Get <var> #
#############

def try_var_name(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].type == TokenType.IDENTIFIER:
        return {"type": "var", "value": code_tokens[code_pointer].value, "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

def try_var_prefix_name(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if caller == "prefixexp" and recursion_depth >= max_recursion_depth: return False

    result = grammar_get_prefixexp(code_tokens, code_pointer, "var", recursion_depth)
    if result == False: return False

    if len(code_tokens) >= 3 and code_tokens[code_pointer + 1].value == ".":
        top = code_tokens.pop(code_pointer)
        mid = code_tokens.pop(code_pointer)
        bottom = code_tokens.pop(code_pointer)

        if bottom.type != TokenType.IDENTIFIER:
            code_tokens.append(bottom)
            bottom = Token()

        new_token = Token(TokenType.IDENTIFIER, top.value + mid.value + bottom.value, top.row, top.col)

        #print("Top:", top, "mid", mid, "bottom", bottom)
        #print("New token:", new_token)

        code_tokens.insert(code_pointer, new_token)

        #print_tokens(code_tokens)

        return {"type": "var", "value": code_tokens[code_pointer].value, "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

def try_var(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    # Try all defined variables
    all_vars = [
        try_var_prefix_name,    # Looks like: <prefiexp> "." [a-z][A-Z]
        try_var_name,           # Looks like: [a-z][A-Z]*
    ]

    # Return with the result
    for index, expression in enumerate(all_vars):
        result = expression(code_tokens, code_pointer, caller, recursion_depth)
        if result != False: return result

    # Default to failure (no var found)
    return False

def grammar_get_var(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    #print(caller, "-> grammar_get_var", recursion_depth)
    if code_pointer < len(code_tokens) and code_tokens[code_pointer].value == "\tEOF": return False

    result = try_var(code_tokens, code_pointer, caller, recursion_depth + 1)

    if result == False: return False
    return result[0], result[1]


#################
# Get <explist> #
#################

def grammar_get_explist(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    #print(caller, "-> grammar_get_explist", recursion_depth)
    if code_pointer < len(code_tokens) and code_tokens[code_pointer].value == "\tEOF": return False

    pointer_offset = 0
    out = []

    #if not is_expression(code_tokens[code_pointer]):
    #    log(f"Explist starts with the wrong type! {code_tokens[code_pointer].place}", "error")
    #    return False

    expected_separator = False
    iter = 0
    while code_pointer + pointer_offset < len(code_tokens) - 1:
        iter += 1
        token = code_tokens[code_pointer + pointer_offset]

        if expected_separator:
            if token.value == ",": # New exp is coming
                expected_separator = False
                pointer_offset += 1
            else:
                break
        else:
            result = grammar_get_exp(code_tokens, code_pointer + pointer_offset, "explist", recursion_depth + 1)

            if result == False:
                log(f"Invalid exp detected! {token.place}", "error")
                return False

            out.append(result[0])
            pointer_offset += result[1]
            expected_separator = True

    if len(out) == 0: return False

    return {"type": "explist", "exps": out}, pointer_offset


#################
# Get <varlist> #
#################

def grammar_get_varlist(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    #print(caller, "-> grammar_get_varlist", recursion_depth)
    if code_pointer < len(code_tokens) and code_tokens[code_pointer].value == "\tEOF": return False

    pointer_offset = 0
    out = []

    #if code_tokens[code_pointer].type != TokenType.IDENTIFIER and code_tokens[code_pointer].value != "(":
    #    log(f"Varlist starts with the wrong type! {code_tokens[code_pointer].place}", "error")
    #    return False


    expected_separator = False
    iter = 0
    while code_pointer + pointer_offset < len(code_tokens) - 1:
        iter += 1
        token = code_tokens[code_pointer + pointer_offset]

        if expected_separator:
            if token.value == ",": # New var is coming
                expected_separator = False
                pointer_offset += 1
            else:
                break
        else:
            result = grammar_get_var(code_tokens, code_pointer + pointer_offset, "varlist", recursion_depth + 1)

            if result == False:
                log(f"Invalid var detected! {token.place}", "error")
                return False

            out.append(result[0])
            pointer_offset += result[1]
            expected_separator = True

    if len(out) == 0: return False

    return {"type": "varlist", "vars": out}, pointer_offset

###################
# Get <statement> #
###################

def try_statement_assignment(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):    
    log_group("Varlist")
    result_varlist = grammar_get_varlist(code_tokens, code_pointer)
    log_group_end()
    if result_varlist == False: return False

    pointer_offset = result_varlist[1]

    log_group("Explist")
    result_explist = grammar_get_explist(code_tokens, code_pointer + pointer_offset + 1)
    log_group_end()
    if result_explist == False: return False

    #print("EXPLIST", result_explist)

    pointer_offset += result_explist[1] + 1

    return {"type": "statement", "stat_type": "assignment", "varlist": result_varlist[0], "explist": result_explist[0]}, code_pointer + pointer_offset

def try_statement_semicolon(code_tokens : list, code_pointer : int, caller = "", recursion_depth = 0):
    if code_tokens[code_pointer].value == ";":
        return {"type": "statement", "stat_type": "semicolon", "value": ";", "row": code_tokens[code_pointer].row, "col": code_tokens[code_pointer].col}, 1

    return False

def try_statement(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    # Try all defined statements
    all_statements = [
        try_statement_semicolon, # Looks like: ";"
        try_statement_assignment, # Looks like: "a.k, b = 'test', 8"
    ]

    # Return with the first result
    for index, statement in enumerate(all_statements):
        result = statement(code_tokens, code_pointer, caller, recursion_depth + 1)
        if result != False: return result

    # Default to failure (no statement found)
    return False

def grammar_get_statement(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    #print(caller, "-> grammar_get_exp", recursion_depth)
    if code_pointer < len(code_tokens) and code_tokens[code_pointer].value == "\tEOF": return False

    result = try_statement(code_tokens, code_pointer, caller, recursion_depth + 1)

    if result == False: return False
    return result[0], result[1]

###############
# Get <block> #
###############

def try_block_statement(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    #print(caller, "-> statement list", recursion_depth)
    if code_pointer < len(code_tokens) and code_tokens[code_pointer].value == "\tEOF": return False

    out = []

    pointer_offset = 0

    iter = 0
    max_iter = 2

    while iter < max_iter and code_pointer + pointer_offset < len(code_tokens):
        current_token = code_tokens[code_pointer + pointer_offset]
        log_group(f"Single statement ({current_token})")
        result = grammar_get_statement(code_tokens, code_pointer + pointer_offset)
        log_group_end()

        if result == False: break

        out.append(result[0])
        pointer_offset += result[1]

        iter += 1

    if iter > max_iter:
        log("Max statement iterations reached!", "error")

    if len(out) == 0: return False
    return out

def grammar_get_block(code_tokens : list, code_pointer : int, caller : str = "", recursion_depth : int = 0):
    log_group("Statement list")
    result = try_block_statement(code_tokens, 0, "block", recursion_depth)
    log_group_end()

    return result

###############
# Get <chunk> #
###############

def grammar_get_chunk(code_tokens : list):
    return grammar_get_block(code_tokens, 0)

def model(code_tokens : list) -> list:
    reset_logs()
    return grammar_get_chunk(code_tokens)

########################################
## Tokenising (preparing compilation) ##
########################################

if __name__ == "__main__":
    print(f"--- Tokenizing: {AQUA}{sys.argv[1]}{WHITE}")

    tokens = []

    try:
        with open(sys.argv[1], "r", encoding="utf8") as f:
            code_string = f.read()

            normalised_code = normalise(code_string)
            pre_tokens = pre_tokenise(normalised_code)
            token_objects = tokenise(pre_tokens)
            print()
            tokens = model(token_objects)

            print_logs()

    except FileNotFoundError as e:
        print(f"{RED}File not found!{WHITE}")
        exit()

    print("\nModel:")

    pp = pprint.PrettyPrinter(width=41, compact=True)
    pp.pprint(tokens)

    if tokens:
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