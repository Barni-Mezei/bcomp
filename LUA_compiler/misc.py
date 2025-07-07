from enum import Enum

RED = "\033[31m"
YELLOW = "\033[93m"
GREEN = "\033[32m"
AQUA = "\033[36m"
GRAY = "\033[90m"
WHITE = "\033[0m"

# Unary operations
UNOP = [
    "-",
    "not",
    "#",
    "~"
]

# Binary operations
BINOP = ["+", "-", "*", "/", "//", "^", "%",
         "&", "~", "|", ">>", "<<", "..",
         "<", "<=", ">", ">=", "==", "~=",
         "and", "or"]

# All operations + assignment
OPERATORS = [
    "="
] + UNOP + BINOP

# Whitespaces
WHITESPACE = [
    " ",
    "\t",
    "\n",
    "\r",
]

PUCTUATION = [
    ".",
    ",",
    ";",
]

# Numerical digits
DIGIT = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
]

# All possible token separators
TOKEN_SEPARATORS = [
    "\n",
    " ",
    ":",
    "...",
    "--",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
] + PUCTUATION + OPERATORS

BLOCK_BOUNDARY = [
    "\n",
    "end"
]

# String boundaries, quotes and multiline strings
STRING_BOUNDARY = [
    "\"",
    "'",
    "[["
    "[=["
]

# All the LUA keywords
KEYWORDS = [
    "and",
    "break",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "goto",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while"
]

class TokenType(Enum):
    UNKNOWN                     = -1
    KEYWORD                     = 0  # while, if
    COMMENT                     = 1  # --
    IDENTIFIER                  = 2  # Variable names
    NUMBER_LITERAL              = 3  # "0.0" or "0." or ".0"
    BOOL_LITERAL                = 4  # true or false
    STRING_LITERAL              = 5  # "string"
    MULTILINE_STRING_LITERAL    = 6  # "string"
    ELLIPSIS                    = 7  # ...
    NIL                         = 8  # nil
    OPERATOR                    = 9  # =
    UNARY_OPERATOR              = 10 # ~, not
    BINARY_OPERATOR             = 11 # +, -, and
    LEFT_PARENTHESIS            = 12 # Like ( { or [
    RIGHT_PARENTHESIS           = 13 # Like ) } or ]
    PUNCTUATION                 = 14 # . , ;
    SPECIAL                     = 99 # The control characters, like EOF


class CharacterPos:
    row : int = 0
    col : int = 0

    def __init__(self, row : int, column : int) -> None:
        self.row = row
        self.col = column

    def __str__(self):
        return f"[Ln {str(self.row + 1)} Col {str(self.col + 1)}]"

class Token:
    type : TokenType = TokenType.UNKNOWN
    value : str = ""
    _place : CharacterPos

    def __init__(self, type : TokenType = TokenType.UNKNOWN, value : str = "", row = -1, col = -1) -> None:
        self.type = type
        self.value = value
        self._place = CharacterPos(row, col)

    @property
    def place(self) -> str:
        return f"[Ln {str(self._place.row + 1)} Col {str(self._place.col + 1)}]"

    @property
    def row(self):
        return self._place.row

    @property
    def col(self):
        return self._place.col

    @property
    def color(self):
        match self.type:
            case TokenType.UNKNOWN:                     return GRAY
            case TokenType.KEYWORD:                     return RED
            case TokenType.COMMENT:                     return GRAY
            case TokenType.IDENTIFIER:                  return WHITE
            case TokenType.NIL:                         return RED
            case TokenType.ELLIPSIS:                    return AQUA
            case TokenType.NUMBER_LITERAL:              return AQUA
            case TokenType.BOOL_LITERAL:                return GREEN
            case TokenType.STRING_LITERAL:              return YELLOW
            case TokenType.MULTILINE_STRING_LITERAL:    return YELLOW
            case TokenType.OPERATOR:                    return AQUA
            case TokenType.UNARY_OPERATOR:              return AQUA
            case TokenType.BINARY_OPERATOR:             return AQUA
            case TokenType.LEFT_PARENTHESIS:            return YELLOW
            case TokenType.RIGHT_PARENTHESIS:           return YELLOW
            case TokenType.PUNCTUATION:                 return GRAY
            case TokenType.SPECIAL:                     return RED

        return WHITE

    def __str__(self):
        text = self.color # Set text color
        text += f"{str(self.type).split('.')[1][:18]:<18}" # Append type enum name
        text += WHITE
        text += f"{self.place:<15} " # Add place in the string

        if self.type == TokenType.SPECIAL: # Print value, colored based on the type
            if self.value == "\tSOF": text += GREEN
            else: text += RED
            text += self.value[1:]
        else:
            text += repr(self.value)

        text += WHITE

        return text
