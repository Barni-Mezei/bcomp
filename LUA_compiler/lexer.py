"""

BUG:
- This code: print(-- [[comment]]"a") should be error, but is: print ( "a" ) this means
that comments effect the next token, regardless of the space between them.

"""

from misc import *
import re

class Lexer:
    string : str = ""
    tokens : list = []

    def __init__(self):
        self._code_pointer = 0

    # Pops a token from self.tokens at the specified index, and returns with the index
    def _remove_token(self, index : int) -> None:
        if index >= 0 and index < len(self.tokens):
            self.tokens.pop(index)
        
        return index

    # Returns with a token type based on the input string
    def get_token_type(self, token_value : str) -> TokenType:
        if token_value in ["\tEOL", "\tEOF", "\tSOF"]: return TokenType.SPECIAL
        if token_value == "nil" or token_value == "NIL": return TokenType.NIL
        if token_value == "true" or token_value == "false": return TokenType.BOOL_LITERAL
        if token_value == "...": return TokenType.ELLIPSIS
        if token_value in KEYWORDS: return TokenType.KEYWORD
        if token_value in OPERATORS: return TokenType.OPERATOR
        if re.search("^\".*\"|\'.*\'$", token_value): return TokenType.STRING_LITERAL
        if re.search("^\\[\\[.*]]|\\[=\\[.*\\]=]$", token_value): return TokenType.MULTILINE_STRING_LITERAL
        if re.search("^(?:(?:(?:[0-9_]+\\.)|(?:\\.[0-9_]+)|(?:[0-9_]+\\.[0-9_]+)|(?:[0-9_]+)|(?:[0-9_]+[eE][0-9_]+))|0[xX][0-9a-fA-F]+|0[bB][01]+)$", token_value): return TokenType.NUMBER_LITERAL
        if re.search("^[a-zA-Z_]\\w*$", token_value): return TokenType.IDENTIFIER
        if token_value == "--": return TokenType.COMMENT
        if token_value in "({[": return TokenType.LEFT_PARENTHESIS
        if token_value in ")}]": return TokenType.RIGHT_PARENTHESIS
        if token_value in PUCTUATION: return TokenType.PUNCTUATION

        return TokenType.UNKNOWN

    # Checks if the sequence can be found in self.string starting from the specified index
    def _check_char_sequence(self, sequence : str, starting_index : int) -> bool:
        return sequence == self.string[starting_index:starting_index + len(sequence)]

    # Works on self.string and splits it in to tokens. The result is stored in self.tokens
    def _scan_string(self):
        was_escaped : bool = False
        was_digit : bool = False
        current_string_boundary : None | str = None

        current_token : str = ""
        current_token_pos = CharacterPos(0, 0)

        self.tokens = []

        index : int = 0
        while index >= 0 and index < len(self.string):
            char = self.string[index]
            index += 1

            # Add char if it was escaped out (only in regular strings)
            if was_escaped:
                was_escaped = False
                if current_string_boundary and len(current_string_boundary) == 1:
                    current_token += char
                    continue

            # Set escape flag
            if char == "\\":
                was_escaped = True
                continue

            # Normal string ends: Close current token and increment row and column positions
            if current_string_boundary and len(current_string_boundary) == 1 and (char == current_string_boundary or char == "\n"):
                current_string_boundary = None
                if not char == "\n": 
                    current_token += char
                self.tokens.append({"value": current_token, "boundary": current_string_boundary, "row": current_token_pos.row, "col": current_token_pos.col})
                current_token_pos.col += len(current_token)

                current_token = ""

                if char == "\n":
                    current_token_pos.row += 1
                    current_token_pos.col = 0
                    was_digit = False

                continue

            # Long string ends: Close current token and increment row and column positions
            if current_string_boundary and len(current_string_boundary) > 1 and self._check_char_sequence(current_string_boundary, index - 1):
                current_token += current_string_boundary
                index += len(current_string_boundary) - 1
                current_string_boundary = None
                self.tokens.append({"value": current_token, "boundary": current_string_boundary, "row": current_token_pos.row, "col": current_token_pos.col})
                current_token_pos.col += len(current_token)

                current_token = ""

                if char == "\n":
                    current_token_pos.row += 1
                    current_token_pos.col = 0
                    was_digit = False

                continue

            # Regular string starts: Set string boundary
            if not current_string_boundary and char in STRING_BOUNDARY:
                current_string_boundary = char
                current_token += char
                continue

            # Multiline string starts: Set string boundary
            if not current_string_boundary and char == "[" and self._check_char_sequence("[[", index - 1):
                current_string_boundary = "]]"
                current_token += "[["
                index += 1
                continue

            # Multiline string starts: Set string boundary
            if not current_string_boundary and char == "[" and self._check_char_sequence("[=[", index - 1):
                current_string_boundary = "]=]"
                current_token += "[=["
                index += 2
                continue

            # Inside a string: Add char to current token
            if current_string_boundary:
                current_token += char
                continue

            # Check if the character is a white space
            if char in WHITESPACE:
                if current_token:
                    self.tokens.append({"value": current_token, "row": current_token_pos.row, "col": current_token_pos.col})
                    current_token_pos.col += len(current_token)

                current_token_pos.col += 1

                current_token = ""

                if char == "\n":
                    current_token_pos.row += 1
                    current_token_pos.col = 0
                    was_digit = False

                continue

            # Check if the character is an operator
            if char in TOKEN_SEPARATORS:
                #Skip dots inside numbers
                if char == "." and was_digit:
                    current_token += char
                    continue

                if current_token:
                    self.tokens.append({"value": current_token, "row": current_token_pos.row, "col": current_token_pos.col})
                    current_token_pos.col += len(current_token)

                self.tokens.append({"value": char, "row": current_token_pos.row, "col": current_token_pos.col})
                current_token_pos.col += 1

                current_token = ""

                continue

            # Otherwise: Add read character to the current token
            current_token += char
        
            was_digit = char in DIGIT

        # Append any "left over" tokens
        if len(current_token) > 0:
            self.tokens.append({"value": current_token, "row": current_token_pos.row, "col": current_token_pos.col})
            current_token_pos.col += len(current_token)
    
        # Insert an extra new line character at the end
        self.tokens.append({"value": "\n", "row": current_token_pos.row, "col": current_token_pos.col})
        self.tokens.append({"value": "\tEOF", "row": current_token_pos.row, "col": current_token_pos.col})


        # Combine multi-token patterns like "==" and ".."
        patterns : list = [t for t in TOKEN_SEPARATORS if len(t) > 1]

        index = 0
        while index >= 0 and index < len(self.tokens):
            # Find and replace patterns
            for pattern in patterns:
                result = False
                for offset, char in enumerate(pattern):
                    if index + offset < len(self.tokens) and self.tokens[index + offset]["value"] == char:
                        result = True
                    else:
                        result = False
                        break

                if result:
                    for _ in range(len(pattern)):
                        self.tokens.pop(index)
    
                    self.tokens.insert(index, {"value": pattern, "row": self.tokens[index]["row"], "col": self.tokens[index]["col"] - len(pattern)})
                    index += len(pattern) - 1
                    break

            index += 1


    # Works on self.tokens and assigns a type to each one of them
    def _eval_tokens(self):
        # Convert to token objects
        for index, t in enumerate(self.tokens):
            self.tokens[index] = Token(self.get_token_type(t["value"]), t["value"], t["row"], t["col"])

        # Join floats
        index : int = 0
        t : Token
        while index >= 0 and index < len(self.tokens):
            t = self.tokens[index]

            # Join tokens if this is a dot and thenext one is a number
            if t.value == "." and index + 1 < len(self.tokens) and self.tokens[index + 1].type == TokenType.NUMBER_LITERAL:
                t.value = t.value + self.tokens[index + 1].value
                self._remove_token(index + 1)
                t.type = self.get_token_type(t.value)

            # Complete number with leading 0 if omitted
            if t.type == TokenType.NUMBER_LITERAL and t.value[0] == ".":
                t.value = "0" + t.value

            # Complete number with trailing 0 if omitted
            if t.type == TokenType.NUMBER_LITERAL and t.value[-1] == ".":
                t.value = t.value + "0"

            index += 1

        # Remove unnecessary tokens like empty lines and comments
        is_in_comment : bool = False
        comment_line : int  = 0

        index = 0
        while index >= 0 and index < len(self.tokens):
            t = self.tokens[index]

            # Skip token if inside a comment
            if is_in_comment:
                if t.row == comment_line:
                    # Remove token if on the same line
                    if t.type == TokenType.MULTILINE_STRING_LITERAL: # End comment if multiline string
                        is_in_comment = False
                        comment_line = 0

                    self._remove_token(index)
                    continue
                else:
                    # New line -> reset comment
                    is_in_comment = False
                    comment_line = 0

            if not is_in_comment and t.type == TokenType.COMMENT:
                is_in_comment = True
                comment_line = t.row
                self._remove_token(index)
                continue

            if t.value in WHITESPACE or t.value == "":
                self._remove_token(index)
                continue

            index += 1

    def tokenise_string(self, input_string : str) -> list:
        self.string = input_string

        self._scan_string()

        self._eval_tokens()

    def tokenise_file(self, file_name : str) -> list:
        with open(file_name, "r", encoding = "utf8") as f: 
            self.string = f.read()

            self._scan_string()

            self._eval_tokens()

# Main script
if __name__ == "__main__":
    lexer = Lexer()

    lexer.tokenise_file("test.lua")

    print("Formatted token view:")
    line_num = 0
    was_token = False
    indent_char = " "
    sep_char = " "
    for t in lexer.tokens:
        if t.row == line_num:
            if was_token:
                print(f"{sep_char}{t.color}{t.value}{WHITE}", end="")
            else:
                print(f"{indent_char*t.col}{t.color}{t.value}{WHITE}", end="")
                was_token = True
        else:
            print("\n" * (t.row - line_num), end = "")
            line_num = t.row
            was_token = False
            if was_token:
                print(f"{sep_char}{t.color}{t.value}{WHITE}", end="")
            else:
                print(f"{indent_char*t.col}{t.color}{t.value}{WHITE}", end="")
                was_token = True