import sys

if "misc" not in sys.modules: from misc import *
if "re" not in sys.modules: import re

class Lexer:
    string : str = ""
    tokens : list = []

    def __init__(self):
        pass

    def _get_next_char(self):
        for c in self.string:
            yield c

        return None

    # Pops a token from self.tokens at the specified index, and returns with the index
    def _remove_token(self, index : int) -> None:
        if index > 0 and index < len(self.tokens):
            self.tokens.pop(index)
        
        return index

    def get_token_type(self, token_value : str) -> TokenType:
        if token_value in ["\tEOL", "\tEOF", "\tSOF"]: return TokenType.SPECIAL
        if token_value == "nil" or token_value == "NIL": return TokenType.NIL
        if token_value == "true" or token_value == "false": return TokenType.BOOL_LITERAL
        if token_value == "...": return TokenType.ELLIPSIS
        if token_value in KEYWORDS: return TokenType.KEYWORD
        if token_value in OPERATORS: return TokenType.OPERATOR
        if re.search("^\".*\"|\'.*\'$", token_value): return TokenType.STRING_LITERAL
        if re.search("^(?:(?:(?:[0-9_]+\\.)|(?:\\.[0-9_]+)|(?:[0-9_]+\\.[0-9_]+)|(?:[0-9_]+)|(?:[0-9_]+[eE][0-9_]+))|0[xX][0-9a-fA-F]+|0[bB][01]+)$", token_value): return TokenType.NUMBER_LITERAL
        if re.search("^[a-zA-Z_]\\w*$", token_value): return TokenType.IDENTIFIER
        if token_value == "--": return TokenType.COMMENT
        if token_value in "({[": return TokenType.LEFT_PARENTHESIS
        if token_value in ")}]": return TokenType.RIGHT_PARENTHESIS

        return TokenType.UNKNOWN

    # Works on self.string and splits it in to tokens. The result is stored in self.tokens
    def _scan_string(self):
        was_escaped : bool = False
        was_digit : bool = False
        current_string_boundary : None|str = None

        current_token : str = ""
        current_token_pos = CharacterPos(0, 0)

        self.tokens = []

        for char in self._get_next_char():
            # Add char if it was escaped out
            if was_escaped:
                current_token += char
                was_escaped = False
                continue

            # Set escape flag
            if char == "\\":
                was_escaped = True
                continue

            # String ends: Close current token and increment row and column positions
            if current_string_boundary and (char == current_string_boundary or char == "\n"):
                current_string_boundary = None
                if char != "\n":
                    current_token += char
                self.tokens.append({"value": current_token, "row": current_token_pos.row, "col": current_token_pos.col})
                current_token_pos.col += len(current_token)

                current_token = ""

                if char == "\n":
                    current_token_pos.row += 1
                    current_token_pos.col = 0

                continue

            # String starts: Set string boundary
            if not current_string_boundary and char in STRING_BOUNDARY:
                current_string_boundary = char
                current_token += char
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
        self.tokens.append({"value": "EOF", "row": current_token_pos.row + 1, "col": current_token_pos.col + 1})

        # Combine multi-token patterns like "=="
        patterns : list = [t for t in TOKEN_SEPARATORS if len(t) > 1]

        index = 0
        for index, t in enumerate(self.tokens):
            # Find and replace patterns
            pattern_found = False
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
    
                    self.tokens.insert(index, {"value": pattern, "row": t["row"], "col": t["col"]})
                    index += len(pattern) - 1
                    pattern_found = True
                    break

    # Works on self.tokens and assigns a type to each one of them
    def _eval_tokens(self):
        # Convert to token objects
        for index, t in enumerate(self.tokens):
            new_token = Token(self.get_token_type(t["value"]), t["value"], t["row"], t["col"])
            self.tokens[index] = new_token


        # Join multiline strings: [[ string ]]
        is_in_multiline_string : bool = False
        multiline_string : Token

        index : int = 0
        t : Token
        while index >= 0 and index < len(self.tokens):
            t = self.tokens[index]

            # Check if starting token
            if not is_in_multiline_string:
                if t.value == "[":
                    if index + 1 < len(self.tokens) and self.tokens[index + 1].value == "[":
                        is_in_multiline_string = True
                        self._remove_token(index)
                        self._remove_token(index)
                        multiline_string = Token(TokenType.STRING_LITERAL, "[[", t.row, t.col)
                        continue

            # Check if strating token
            if is_in_multiline_string:
                if t.value == "]":
                    if index + 1 < len(self.tokens) and self.tokens[index + 1].value == "]":
                        is_in_multiline_string = False
                        self._remove_token(index)
                        self._remove_token(index)
                        multiline_string.value += "]]"
                        self.tokens.insert(index, multiline_string)
                        continue
                else:
                    multiline_string.value += t.value
                    self._remove_token(index)
                    continue

            index += 1

        for t in self.tokens:
            print(f"T: {t}")

        # Remove unnecessary tokens like empty lines and comments
        is_in_comment : bool = False
        comment_line : int  = 0

        index : int = 0
        t : Token
        while index >= 0 and index < len(self.tokens):
            t = self.tokens[index]

            # Skip token if inside a comment
            if is_in_comment:
                if t.row == comment_line:
                    # Remove token if on the same line
                    if t.type == TokenType.STRING_LITERAL and t.value[0] == "[": # End comment if multiline string
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

        # Print scanned tokens
        print("Scan result ----------")
        line_num = 0
        was_token = False
        for t in self.tokens:
            if t["row"] == line_num:
                if was_token:
                    print(f" {t['value']}", end="")
                else:
                    print(f"{t['value']}", end="")
                    was_token = True
            else:
                line_num = t["row"]
                was_token = False
                if was_token:
                    print(f" {t['value']}", end="")
                else:
                    print(f"\n{t['value']}", end="")
                    was_token = True
        print("----------------------")

        self._eval_tokens()

        # Print evaluated
        print("Eval result ----------")
        line_num = 0
        was_token = False
        for t in self.tokens:
            print(t)
        print("----------------------")

if __name__ == "__main__":
    lexer = Lexer()
    
    f = open("test.lua", "r", encoding="utf8")

    #for c in f.read():
    #    print(repr(c))

    lexer.tokenise_string(f.read())
