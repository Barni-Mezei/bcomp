import sys

# Import compiler data
if "misc" not in sys.modules: from misc import *

class Lexer:
    char_index : int = 0
    input_length : int = 0
    string : str = ""
    tokens : list = []

    def __init__(self):
        self.char_index = 0

    def _get_next_char(self):
        for c in self.string:
            yield c

        return None

    def _scan_string(self) -> list:
        self.char_index = 0

        was_escaped : bool = False
        current_string_boundary : None|str = None

        current_token : str = ""
        current_token_pos = CharacterPos(0, 0)

        output : list = []

        for char in self._get_next_char():
            print(f"Char: '{char}'")

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
                current_token += char
                output.append({"token": current_token, "separator": " ", "row": current_token_pos.row, "col": current_token_pos.col})
                current_token_pos.col += len(current_token) + 1

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

            # Check if the character is a token separator
            if char in TOKEN_SEPARATORS:
                output.append({"token": current_token, "separator": char, "row": current_token_pos.row, "col": current_token_pos.col})
                current_token_pos.col += len(current_token) + 1

                current_token = ""

                if char == "\n":
                    current_token_pos.row += 1
                    current_token_pos.col = 0

                continue

            # Otherwise: Add read character to the current token
            if not char in [" ", "\t"]:
                current_token += char
        
        # Insert an extra new line character at the end
        if len(current_token) > 0:
            output.append({"token": current_token, "separator": "\n", "row": current_token_pos.row, "col": current_token_pos.col})

        return output
    
    def tokenise_string(self, input_string : str) -> list:
        self.string = input_string

        output = self._scan_string()

        print(output)

if __name__ == "__main__":
    lexer = Lexer()
    lexer.tokenise_string("""print("Hel		lo,
	world!")""")
